from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
from neo4j_config import NEO4J_DATABASE, get_driver

app = FastAPI(title="EvoluiPC API", description="Motor Inteligente de Hardware")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginData(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
def login(data: LoginData):
    return {"token": "token-evoluipc-123", "user": {"username": data.username}}

@app.get("/api/auth/me")
def get_me():
    return {"user": {"username": "Victor Torres"}}

@app.get("/api/machine/me")
def get_machine():
    return {
        "machine": {
            "cpu": "Ryzen 5 2600",
            "gpu": "GTX 1060 6GB",
            "ram": "16GB DDR4",
            "storage": "SSD SATA 500GB",
            "motherboard": "ASUS PRIME A320M-K/BR",
            "psu": "500W",
            "bottleneck": "CPU e GPU"
        },
        "diagnostics": [
            "Sua placa-mãe atual (AM4) suporta upgrades poderosos mediante atualização de BIOS.",
            "O processador e a placa de vídeo antigos podem sofrer quedas de FPS em jogos modernos.",
            "Recomendamos um upgrade focado na plataforma existente antes de trocar a placa-mãe."
        ]
    }

@app.get("/api/upgrade-route/me")
def get_route():
    return {
        "route": [
            {"step": "Passo 1", "action": "Atualizar a BIOS da ASUS PRIME A320M-K/BR", "impact": "Prepara o terreno para a nova geração AM4"},
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