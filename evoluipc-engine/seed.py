from neo4j_config import NEO4J_DATABASE, get_driver

def popular_banco():
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            print("Limpando banco antigo...")
            session.run("MATCH (n) DETACH DELETE n")

            print("Plantando Placas-mãe...")
            session.run("CREATE (:PlacaMae {nome: 'ASUS PRIME A320M-K/BR', soquete: 'AM4', ram_tipo: 'DDR4'})")
            session.run("CREATE (:PlacaMae {nome: 'Gigabyte B550M AORUS', soquete: 'AM4', ram_tipo: 'DDR4'})")

            print("Plantando Processadores...")
            session.run("CREATE (:Processador {nome: 'AMD Ryzen 7 5700X3D', soquete: 'AM4', preco: 1350, tier: 'High-End'})")
            session.run("CREATE (:Processador {nome: 'AMD Ryzen 5 5600', soquete: 'AM4', preco: 850, tier: 'Mid-Range'})")

            print("Plantando Placas de Vídeo (GPUs)...")
            session.run("CREATE (:PlacaDeVideo {nome: 'NVIDIA RTX 4060 8GB', preco: 1800, tier: 'Mid-High'})")
            session.run("CREATE (:PlacaDeVideo {nome: 'AMD Radeon RX 6600 8GB', preco: 1300, tier: 'Mid-Range'})")

            print("Criando laços de compatibilidade (A Mágica dos Grafos)...")
            session.run("""
            MATCH (p:Processador), (m:PlacaMae)
            WHERE p.soquete = m.soquete
            MERGE (p)-[:COMPATIVEL_COM]->(m)
            """)

            print(f"Sucesso! O Neo4j '{NEO4J_DATABASE}' está abastecido com hardware real.")

if __name__ == "__main__":
    popular_banco()