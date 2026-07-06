"""
Driver HTTP compativel com a interface basica do driver oficial `neo4j`,
usando a Query API do Neo4j Aura (HTTPS, porta 443) em vez do protocolo
Bolt (porta 7687).

Motivo: o Render (e outros PaaS no plano free) bloqueia conexoes TCP de
saida em portas nao padrao, incluindo a 7687 usada pelo Bolt. A Query API
roda inteiramente sobre HTTPS na porta 443, que e sempre liberada.

Usamos o formato "Plain JSON" da Query API (o default, quando nenhum
Accept especial e enviado), onde nos e cada registro vem como:
    {"elementId": "...", "labels": [...], "properties": {...}}
e valores escalares (strings, numeros, bool, listas, mapas) vem direto,
sem nenhum envelope de tipo. O envelope {"$type": ..., "_value": ...}
so existe no formato "Typed JSON" (Accept: application/vnd.neo4j.query.v1.1),
que NAO usamos aqui.

Uso (compatibilidade com o codigo existente):

    driver = get_driver()
    with driver.session(database=NEO4J_DATABASE) as session:
        record = session.run(query, **params).single()
        records = session.run(query, **params).data()
        records = list(session.run(query, **params))

Documentacao oficial da Query API:
https://neo4j.com/docs/query-api/current/
https://neo4j.com/docs/aura/connecting-applications/query-api/
"""
import requests


class HttpQueryError(Exception):
    """Erro generico ao executar uma query via HTTP Query API."""

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class ServiceUnavailable(HttpQueryError):
    """Equivalente ao neo4j.exceptions.ServiceUnavailable: erro de rede/conexao/indisponibilidade."""


class Neo4jHttpError(HttpQueryError):
    """Equivalente generico ao neo4j.exceptions.Neo4jError: erro retornado pelo banco (sintaxe, constraint, etc)."""


def _normalize_uri(uri):
    """
    Converte uris no formato neo4j+s://<host>, neo4j://<host> ou
    bolt://<host> para a base HTTPS usada pela Query API. Aceita tambem
    uris ja em https://.
    """
    if uri.startswith("https://"):
        return uri.rstrip("/")
    if "://" in uri:
        host = uri.split("://", 1)[1]
    else:
        host = uri
    host = host.split("/")[0].split(":")[0]
    return f"https://{host}"


class _Record(dict):
    """
    Dict que aceita record["chave"] e dict(record). Mantido como classe
    separada apenas para clareza semantica no resto do codigo.
    """
    pass


class _Result:
    """Substitui o objeto Result do driver oficial: .single(), .data(), iteravel."""

    def __init__(self, records):
        self._records = [_Record(r) for r in records]

    def single(self):
        return self._records[0] if self._records else None

    def data(self):
        return list(self._records)

    def __iter__(self):
        return iter(self._records)

    def __len__(self):
        return len(self._records)


class _HttpSession:
    def __init__(self, base_url, auth, database):
        self._base_url = base_url
        self._auth = auth
        self._database = database

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def run(self, query, **params):
        url = f"{self._base_url}/db/{self._database}/query/v2"
        body = {"statement": query, "parameters": params}

        try:
            response = requests.post(
                url,
                json=body,
                auth=self._auth,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=30,
            )
        except requests.exceptions.RequestException as exc:
            # Falha de rede/DNS/timeout: equivalente ao ServiceUnavailable do driver Bolt.
            raise ServiceUnavailable(
                f"Falha de rede ao acessar Neo4j Aura via HTTPS: {exc}"
            ) from exc

        # Erros de autenticacao e indisponibilidade chegam com status HTTP != 2xx.
        if response.status_code == 401:
            raise Neo4jHttpError(
                "Credenciais invalidas para o Neo4j Aura (HTTP 401).",
                status_code=401,
                payload=_safe_json(response),
            )

        if response.status_code >= 500 or response.status_code == 503:
            raise ServiceUnavailable(
                f"Neo4j Aura indisponivel (HTTP {response.status_code}).",
                status_code=response.status_code,
                payload=_safe_json(response),
            )

        payload = _safe_json(response)

        # Mesmo com status 2xx, a Query API pode reportar erros no corpo
        # (ex.: erro de sintaxe Cypher, constraint violation, etc).
        errors = payload.get("errors") if isinstance(payload, dict) else None
        if errors:
            first_error = errors[0]
            raise Neo4jHttpError(
                f"Erro Cypher retornado pela Query API: "
                f"{first_error.get('code', 'desconhecido')} - {first_error.get('message', '')}",
                status_code=response.status_code,
                payload=payload,
            )

        if response.status_code >= 400:
            raise Neo4jHttpError(
                f"Erro inesperado na Query API (HTTP {response.status_code}): {response.text[:500]}",
                status_code=response.status_code,
                payload=payload,
            )

        data = (payload or {}).get("data", {})
        fields = data.get("fields", [])
        values_rows = data.get("values", [])

        records = []
        for row in values_rows:
            record = dict(zip(fields, row))
            records.append(record)

        return _Result(records)


def _safe_json(response):
    try:
        return response.json()
    except ValueError:
        return {}


class _HttpDriver:
    def __init__(self, uri, auth):
        self._base_url = _normalize_uri(uri)
        self._auth = auth

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def close(self):
        pass

    def session(self, database="neo4j", **kwargs):
        return _HttpSession(self._base_url, self._auth, database)


class HttpGraphDatabase:
    """Substituto drop-in de neo4j.GraphDatabase, usado apenas para criar o driver HTTP."""

    @staticmethod
    def driver(uri, auth=None, **kwargs):
        return _HttpDriver(uri, auth)