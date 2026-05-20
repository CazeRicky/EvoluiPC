from django.core.management.base import BaseCommand
from neo4j import GraphDatabase
import os


class Command(BaseCommand):
    help = "Popula o Neo4j com dados de hardware (CPUs, placas-mãe) para recomendações"

    def handle(self, *args, **options):
        uri = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "evoluipc123")
        
        driver = GraphDatabase.driver(uri, auth=(user, password))

        with driver.session() as session:
            # Criar sockets
            self.stdout.write("Criando sockets...")
            session.run("""
                CREATE (s1:Socket {name: "LGA1700"})
                CREATE (s2:Socket {name: "AM5"})
                CREATE (s3:Socket {name: "BGA1744"})
            """)

            # Criar placas-mãe Desktop
            self.stdout.write("Criando placas-mãe Desktop...")
            session.run("""
                MATCH (s:Socket {name: "LGA1700"})
                CREATE (mb:Motherboard {name: "A320M", socket: "LGA1700", type: "Desktop"})
                CREATE (mb)-[:HAS_SOCKET]->(s)
            """)

            # Criar placas-mãe Notebook (virtual - pois não são atualizáveis)
            self.stdout.write("Criando placas-mãe Notebook...")
            session.run("""
                CREATE (mbnt:Motherboard {name: "Placa-mãe Notebook", socket: "BGA1744", type: "Laptop"})
            """)

            # Criar processadores Desktop (Intel)
            self.stdout.write("Criando processadores Desktop...")
            session.run("""
                MATCH (s:Socket {name: "LGA1700"})
                CREATE (cpu1:Processor {name: "Intel i5-10400", performance_score: 4500, price: 450.00, socket: "LGA1700", type: "Desktop"})
                CREATE (cpu1)-[:FITS_IN]->(s)
                
                CREATE (cpu2:Processor {name: "Intel i5-12400", performance_score: 6500, price: 650.00, socket: "LGA1700", type: "Desktop"})
                CREATE (cpu2)-[:FITS_IN]->(s)
                
                CREATE (cpu3:Processor {name: "Intel i7-13700K", performance_score: 9500, price: 1200.00, socket: "LGA1700", type: "Desktop"})
                CREATE (cpu3)-[:FITS_IN]->(s)
            """)

            # Criar processadores Notebook (Intel - apenas para referência, não são atualizáveis)
            self.stdout.write("Criando processadores Notebook...")
            session.run("""
                CREATE (cpu_nb1:Processor {name: "Intel Core i5-12450H", performance_score: 7500, price: 800.00, socket: "BGA1744", type: "Laptop"})
                CREATE (cpu_nb2:Processor {name: "Intel Core i7-12700H", performance_score: 8500, price: 1100.00, socket: "BGA1744", type: "Laptop"})
                CREATE (cpu_nb3:Processor {name: "Intel Core i9-13900H", performance_score: 9800, price: 1500.00, socket: "BGA1744", type: "Laptop"})
            """)

            self.stdout.write(self.style.SUCCESS("✓ Hardware seed concluído com sucesso!"))

        driver.close()
