<<<<<<< HEAD
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()
=======
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
from neo4j_config import NEO4J_DATABASE, get_driver
>>>>>>> 4c52f0495ecc34ce3be4d35d8c2e7ddd6dfd5379

app = FastAPI(title="EvoluiPC API", description="Motor Inteligente de Hardware")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

=======
>>>>>>> 4c52f0495ecc34ce3be4d35d8c2e7ddd6dfd5379
class LoginData(BaseModel):
    username: str
    password: str

<<<<<<< HEAD
=======
class HardwareUpload(BaseModel):
    username: str
    hardware: dict

>>>>>>> 4c52f0495ecc34ce3be4d35d8c2e7ddd6dfd5379
@app.post("/api/auth/login")
def login(data: LoginData):
    return {"token": "token-evoluipc-123", "user": {"username": data.username}}

@app.get("/api/auth/me")
<<<<<<< HEAD
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
=======
def get_me(username: str = "Visitante"):
    return {"user": {"username": username}}

@app.post("/api/machine/upload")
def receber_hardware(dados: HardwareUpload):
    machine_data = {
        "cpu": dados.hardware.get("cpu", "Desconhecido"),
        "gpu": dados.hardware.get("gpu", "Desconhecida"),
        "motherboard": dados.hardware.get("motherboard", "Desconhecida"),
        "ram": dados.hardware.get("ram", "Desconhecida"),
        "socket": "Detectado",
        "ram_type": "DDR4/DDR5",
        "storage": "Detectado pelo Agente"
    }
    
    diagnostics = [
        f"✅ Sincronizado com o Agente EvoluiPC!",
        f"Hardware real de {dados.username} detectado com sucesso.",
        f"Placa-mãe: {machine_data['motherboard']}."
    ]
    
    query = """
    MATCH (u:AppUser {username: $username})
    MERGE (u)-[:HAS_PC_PARTS]->(p:UserPcParts)
    SET p.machine_json = $machine_json,
        p.diagnostics_json = $diagnostics_json,
        p.source = 'Scanner_Local_Exe',
        p.updated_at = $now
    RETURN p
    """
    
    try:
        with get_driver() as driver:
            with driver.session(database=NEO4J_DATABASE) as session:
                resultado = session.run(
                    query,
                    username=dados.username,
                    machine_json=json.dumps(machine_data, ensure_ascii=False),
                    diagnostics_json=json.dumps(diagnostics, ensure_ascii=False),
                    now=datetime.now(timezone.utc).isoformat()
                )
                
                if resultado.single():
                    return {"status": "Hardware real gravado com sucesso no formato do site!"}
                else:
                    return {"status": f"Erro: Usuário '{dados.username}' não encontrado no Neo4j."}
    except Exception as e:
        return {"status": f"Falha na conexão: {str(e)}"}

@app.get("/api/machine/me")
def get_machine(username: str = "Visitante"):
    query = """
    MATCH (u:AppUser {username: $username})-[:HAS_PC_PARTS]->(p:UserPcParts)
    RETURN p.machine_json AS machine_json, p.diagnostics_json AS diagnostics_json
    """
    
    try:
        with get_driver() as driver:
            with driver.session(database=NEO4J_DATABASE) as session:
                record = session.run(query, username=username).single()
                
                if record:
                    m_json = record["machine_json"]
                    d_json = record["diagnostics_json"]
                    
                    return {
                        "machine": json.loads(m_json) if isinstance(m_json, str) else m_json,
                        "diagnostics": json.loads(d_json) if isinstance(d_json, str) else d_json
                    }
    except Exception:
        pass 
        
    return {
        "machine": {"cpu": "Aguardando Scanner...", "gpu": "Aguardando Scanner..."},
        "diagnostics": [f"Nenhum hardware real encontrado para {username}."]
    }

@app.get("/api/upgrade-route/me")
def get_route(username: str = "Visitante"):
    return {
        "route": [
            {"step": "Passo 1", "action": "Atualizar a BIOS", "impact": "Estabilidade"},
            {"step": "Passo 2", "action": "Instalar Ryzen 5000", "impact": "Ganho de Performance"},
            {"step": "Passo 3", "action": "Nova GPU", "impact": "Fim do Gargalo"}
>>>>>>> 4c52f0495ecc34ce3be4d35d8c2e7ddd6dfd5379
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
<<<<<<< HEAD
    
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            with driver.session() as session:
                resultado = session.run(query)
                for reg in resultado:
                    catalog.append({
                        "name": reg["nome"],
                        "price": f"R$ {reg['preco']},00",
                        "source": "Lojas Parceiras",
                        "tag": f"Upgrade Ideal de {reg['tipo']}"
                    })
    except Exception as e:
        catalog = [{"name": "Falha na conexão com Neo4j", "price": "-", "source": "Erro", "tag": str(e)}]

=======
    try:
        with get_driver() as driver:
            with driver.session(database=NEO4J_DATABASE) as session:
                for reg in session.run(query):
                    catalog.append({
                        "name": reg["nome"], "price": f"R$ {reg['preco']},00", "source": "Lojas", "tag": f"Upgrade {reg['tipo']}", "origin": "neo4j"
                    })
    except Exception:
        pass
>>>>>>> 4c52f0495ecc34ce3be4d35d8c2e7ddd6dfd5379
    return {"catalog": catalog}