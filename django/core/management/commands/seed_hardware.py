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
            # Limpar dados antigos (opcional, comentado para debug)
            # self.stdout.write("Limpando dados antigos...")
            # session.run("MATCH (n) DETACH DELETE n")

            # Criar sockets
            self.stdout.write("Criando sockets...")
            session.run("""
                CREATE (s1:Socket {name: "LGA1700"})
                CREATE (s2:Socket {name: "AM5"})
                CREATE (s3:Socket {name: "BGA1744"})
            """)

            # Criar placas-mãe Desktop (LGA1700)
            self.stdout.write("Criando placas-mãe Desktop LGA1700...")
            session.run("""
                MATCH (s:Socket {name: "LGA1700"})
                CREATE (mb1:Motherboard {name: "A320M", socket: "LGA1700", type: "Desktop"})
                CREATE (mb1)-[:HAS_SOCKET]->(s)
                CREATE (mb2:Motherboard {name: "B660M", socket: "LGA1700", type: "Desktop"})
                CREATE (mb2)-[:HAS_SOCKET]->(s)
                CREATE (mb3:Motherboard {name: "Z790", socket: "LGA1700", type: "Desktop"})
                CREATE (mb3)-[:HAS_SOCKET]->(s)
            """)

            # Criar placas-mãe Desktop (AM5)
            self.stdout.write("Criando placas-mãe Desktop AM5...")
            session.run("""
                MATCH (s:Socket {name: "AM5"})
                CREATE (mb1:Motherboard {name: "A620M", socket: "AM5", type: "Desktop"})
                CREATE (mb1)-[:HAS_SOCKET]->(s)
                CREATE (mb2:Motherboard {name: "B650", socket: "AM5", type: "Desktop"})
                CREATE (mb2)-[:HAS_SOCKET]->(s)
            """)

            # Criar placas-mãe Notebook (BGA1744)
            self.stdout.write("Criando placas-mãe Notebook...")
            session.run("""
                CREATE (mbnt:Motherboard {name: "Placa-mãe Notebook", socket: "BGA1744", type: "Laptop"})
            """)

            # Criar processadores Desktop Intel LGA1700 - Geração 10-13
            self.stdout.write("Criando processadores Desktop Intel...")
            session.run("""
                MATCH (s:Socket {name: "LGA1700"})
                CREATE (cpu1:Processor {name: "Intel i3-10100", performance_score: 3500, price: 250.00, socket: "LGA1700", type: "Desktop"})
                CREATE (cpu1)-[:FITS_IN]->(s)
                
                CREATE (cpu2:Processor {name: "Intel i5-10400", performance_score: 4500, price: 450.00, socket: "LGA1700", type: "Desktop"})
                CREATE (cpu2)-[:FITS_IN]->(s)
                
                CREATE (cpu3:Processor {name: "Intel i5-12400", performance_score: 6500, price: 650.00, socket: "LGA1700", type: "Desktop"})
                CREATE (cpu3)-[:FITS_IN]->(s)
                
                CREATE (cpu4:Processor {name: "Intel i7-12700", performance_score: 8200, price: 950.00, socket: "LGA1700", type: "Desktop"})
                CREATE (cpu4)-[:FITS_IN]->(s)
                
                CREATE (cpu5:Processor {name: "Intel i7-13700K", performance_score: 9500, price: 1200.00, socket: "LGA1700", type: "Desktop"})
                CREATE (cpu5)-[:FITS_IN]->(s)
                
                CREATE (cpu6:Processor {name: "Intel i9-13900K", performance_score: 11000, price: 1800.00, socket: "LGA1700", type: "Desktop"})
                CREATE (cpu6)-[:FITS_IN]->(s)
            """)

            # Criar processadores Desktop AMD AM5
            self.stdout.write("Criando processadores Desktop AMD...")
            session.run("""
                MATCH (s:Socket {name: "AM5"})
                CREATE (cpu1:Processor {name: "AMD Ryzen 5 5500", performance_score: 4200, price: 400.00, socket: "AM5", type: "Desktop"})
                CREATE (cpu1)-[:FITS_IN]->(s)
                
                CREATE (cpu2:Processor {name: "AMD Ryzen 5 7500", performance_score: 6800, price: 700.00, socket: "AM5", type: "Desktop"})
                CREATE (cpu2)-[:FITS_IN]->(s)
                
                CREATE (cpu3:Processor {name: "AMD Ryzen 7 7700", performance_score: 8500, price: 1100.00, socket: "AM5", type: "Desktop"})
                CREATE (cpu3)-[:FITS_IN]->(s)
                
                CREATE (cpu4:Processor {name: "AMD Ryzen 9 7900X", performance_score: 10200, price: 1600.00, socket: "AM5", type: "Desktop"})
                CREATE (cpu4)-[:FITS_IN]->(s)
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
