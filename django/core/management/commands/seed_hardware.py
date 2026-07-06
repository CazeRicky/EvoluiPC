from django.core.management.base import BaseCommand
from core.neo4j_http_driver import HttpGraphDatabase as GraphDatabase
import os


class Command(BaseCommand):
    help = "Popula o Neo4j com dados de hardware (CPUs, placas-mãe) para recomendações"

    def handle(self, *args, **options):
        uri = os.environ["NEO4J_URI"]
        user = os.environ["NEO4J_USER"]
        password = os.environ["NEO4J_PASSWORD"]
        database = os.environ.get("NEO4J_DATABASE", "neo4j")

        driver = GraphDatabase.driver(uri, auth=(user, password))

        with driver.session(database=database) as session:
            # Criar sockets
            self.stdout.write("Criando sockets...")
            session.run("""
                CREATE (s1:Socket {name: "LGA1700"})
                CREATE (s2:Socket {name: "AM5"})
            """)

            # Criar placas-mãe
            self.stdout.write("Criando placas-mãe...")
            session.run("""
                MATCH (s:Socket {name: "LGA1700"})
                CREATE (mb:Motherboard {name: "A320M", socket: "LGA1700"})
                CREATE (mb)-[:HAS_SOCKET]->(s)
            """)

            # Criar processadores básicos (i5-10400, i5-12400, i7-13700K)
            self.stdout.write("Criando processadores...")
            session.run("""
                MATCH (s:Socket {name: "LGA1700"})
                CREATE (cpu1:Processor {name: "Intel i5-10400", performance_score: 4500, price: 450.00, socket: "LGA1700"})
                CREATE (cpu1)-[:FITS_IN]->(s)

                CREATE (cpu2:Processor {name: "Intel i5-12400", performance_score: 6500, price: 650.00, socket: "LGA1700"})
                CREATE (cpu2)-[:FITS_IN]->(s)

                CREATE (cpu3:Processor {name: "Intel i7-13700K", performance_score: 9500, price: 1200.00, socket: "LGA1700"})
                CREATE (cpu3)-[:FITS_IN]->(s)
            """)

            self.stdout.write(self.style.SUCCESS("✓ Hardware seed concluído com sucesso!"))

        driver.close()