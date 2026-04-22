import json
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

class HardwareUpload(BaseModel):
    username: str
    hardware: dict

@app.post("/api/auth/login")
def login(data: LoginData):
    return {"token": "token-evoluipc-123", "user": {"username": data.username}}

@app.get("/api/auth/me")
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
    try:
        with get_driver() as driver:
            with driver.session(database=NEO4J_DATABASE) as session:
                for reg in session.run(query):
                    catalog.append({
                        "name": reg["nome"], "price": f"R$ {reg['preco']},00", "source": "Lojas", "tag": f"Upgrade {reg['tipo']}", "origin": "neo4j"
                    })
    except Exception:
        pass
    return {"catalog": catalog}