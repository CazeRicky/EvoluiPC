from pathlib import Path
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


ENGINE_DIR = Path(__file__).resolve().parent
load_dotenv(ENGINE_DIR / ".env")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "EvoluiPC")


def get_driver():
    if not NEO4J_PASSWORD:
        raise RuntimeError(
            "NEO4J_PASSWORD nao configurado. Crie evoluipc-engine/.env com as credenciais do Neo4j."
        )

    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))