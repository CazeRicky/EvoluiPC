from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
from neo4j_config import NEO4J_DATABASE, get_driver # Estrutura nova do Docker

app = FastAPI(title="EvoluiPC API", description="Motor Inteligente de Hardware")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mantendo o seu banco de memória para o Scanner
maquinas_escaneadas = {}

class LoginData(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
def login(data: LoginData):
    return {"token": "token-evoluipc-123", "user": {"username": data.username}}

@app.get("/api/auth/me")
def get_me():
    return {"user": {"username": "Victor"}}

# Rota do seu Scanner Local
class HardwareUpload(BaseModel):
    username: str
    hardware: dict

@app.post("/api/machine/upload")
def receber_hardware(dados: HardwareUpload):
    maquinas_escaneadas[dados.username] = dados.hardware
    return {"status": "Hardware recebido com sucesso!"}

@app.get("/api/machine/me")
def get_machine():
    usuario_logado = "Victor" 
    
    # Lógica que integra o seu Scanner com a resposta da API
    if usuario_logado in maquinas_escaneadas:
        pc_real = maquinas_escaneadas[usuario_logado]
        return {
            "machine": {
                "cpu": pc_real.get("cpu", "Desconhecido"),
                "gpu": pc_real.get("gpu", "Desconhecida"),
                "ram": pc_real.get("ram", "Desconhecida"),
                "storage": "A Verificar", 
                "motherboard": pc_real.get("motherboard", "Desconhecida"),
                "psu": "A Verificar",
                "bottleneck": "Calculando..."
            },
            "diagnostics": [
                "✅ Hardware real detectado com sucesso pelo Agente EvoluiPC!",
                f"Sua placa-mãe identificada é a {pc_real.get('motherboard')}.",
                "O Motor Neo4j está analisando a melhor rota de upgrade para sua configuração."
            ]
        }
        
    return {
        "machine": {
            "cpu": "Aguardando Scanner...",
            "gpu": "Aguardando Scanner...",
            "ram": "Aguardando Scanner...",
            "storage": "-",
            "motherboard": "-",
            "psu": "-",
            "bottleneck": "-"
        },
        "diagnostics": [
            "⚠️ Nenhum hardware detectado. Por favor, rode o Agente EvoluiPC na sua máquina."
        ]
    }

@app.get("/api/upgrade-route/me")
def get_route():
    return {
        "route": [
            {"step": "Passo 1", "action": "Atualizar a BIOS", "impact": "Prepara o terreno para a nova geração AM4"},
            {"step": "Passo 2", "action": "Instalar o Ryzen 7 5700X3D", "impact": "Salto extremo em FPS e estabilidade de sistema"},
            {"step": "Passo 3", "action": "Adicionar a RTX 4060", "impact": "Gargalo resolvido. Gráficos no Ultra em 1080p."}
        ]
    }

@app.get("/api/recommendations/me")
def get_recommendations():
    query = """
    MATCH (p:Processador) RETURN p.nome AS nome, p.preco AS preco, 'CPU' as tipo
    UNION ALL
    MATCH (g:PlacaDeVideo) RETURN g.nome AS nome, g.preco AS preco, 'GPU' as tipo
    """
    catalog = []
    meta = {
        "provider": "neo4j",
        "database": NEO4J_DATABASE,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "query": "catalog_v1",
        "count": 0,
    }
    
    try:
        # Usando a conexão nova via Driver do Docker
        with get_driver() as driver:
            with driver.session(database=NEO4J_DATABASE) as session:
                resultado = session.run(query)
                for reg in resultado:
                    catalog.append({
                        "name": reg["nome"],
                        "price": f"R$ {reg['preco']},00",
                        "source": "Lojas Parceiras",
                        "tag": f"Upgrade Ideal de {reg['tipo']}",
                        "origin": "neo4j",
                    })
        meta["count"] = len(catalog)
    except Exception as e:
        catalog = [{"name": "Falha na conexão com Neo4j", "price": "-", "source": "Erro", "tag": str(e), "origin": "error"}]
        meta = {
            "provider": "engine-error",
            "database": NEO4J_DATABASE,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "query": "catalog_v1",
            "count": 0,
            "error": str(e),
        }

    return {"catalog": catalog, "meta": meta}