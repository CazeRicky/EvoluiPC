import json
import os
from neo4j_config import get_driver, NEO4J_DATABASE

def popular_banco():
    caminho_json = 'hardware.json'
    
    if not os.path.exists(caminho_json):
        print(f"❌ Erro: '{caminho_json}' não encontrado. Rode o etl.py primeiro!")
        return

    with open(caminho_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    print("Injetando dados no Neo4j...")

    q_limpeza = "MATCH (n) WHERE n:Processador OR n:PlacaMae OR n:PlacaDeVideo DETACH DELETE n"
    
    q_cpus = """
    UNWIND $batch AS cpu
    MERGE (p:Processador {nome: cpu.nome})
    SET p.soquete = cpu.soquete, p.tier = cpu.tier, p.preco = cpu.preco
    """
    
    q_gpus = """
    UNWIND $batch AS gpu
    MERGE (g:PlacaDeVideo {nome: gpu.nome})
    SET g.tier = gpu.tier, g.preco = gpu.preco
    """
    
    q_mbs = """
    UNWIND $batch AS mb
    MERGE (m:PlacaMae {nome: mb.nome})
    SET m.soquete = mb.soquete, m.ram_tipo = mb.ram_tipo, m.preco = mb.preco
    """

    q_relacoes = """
    MATCH (c:Processador), (m:PlacaMae)
    WHERE c.soquete = m.soquete
    MERGE (c)-[:COMPATIVEL_COM]->(m)
    """

    try:
        with get_driver() as driver:
            with driver.session(database=NEO4J_DATABASE) as session:
                session.run(q_limpeza)
                session.run(q_cpus, batch=dados.get("processadores", []))
                session.run(q_gpus, batch=dados.get("placas_de_video", []))
                session.run(q_mbs, batch=dados.get("placas_mae", []))
                session.run(q_relacoes)
                
        print("✅ Banco populado com sucesso! As relações de compatibilidade foram criadas.")
    except Exception as e:
        print(f"❌ Erro no Neo4j: {e}")

if __name__ == "__main__":
    popular_banco()