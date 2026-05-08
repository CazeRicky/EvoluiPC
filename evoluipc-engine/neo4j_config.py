from pathlib import Path
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


ENGINE_DIR = Path(__file__).resolve().parent
load_dotenv(ENGINE_DIR / ".env")


NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


def get_driver():
    if not NEO4J_URI:
        raise RuntimeError("NEO4J_URI não configurado.")

    if not NEO4J_PASSWORD:
        raise RuntimeError("NEO4J_PASSWORD não configurado.")

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )

    return driver


if __name__ == "__main__":
    try:
        with get_driver() as driver:
            driver.verify_connectivity()
            print("✅ Conexão com Neo4j Aura funcionando.")
    except Exception as e:
        print(f"❌ Erro ao conectar no Neo4j Aura: {e}")