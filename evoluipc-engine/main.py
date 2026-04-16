from neo4j_config import NEO4J_DATABASE, get_driver

def criar_setup_inicial(driver):
    query = """
    // 1. Cria o Processador
    MERGE (cpu:Processador {nome: 'Ryzen 7 5700X3D'})
    SET cpu.soquete = 'AM4', cpu.tdp = 105, cpu.performance = 8500
    
    // 2. Cria a Placa-mãe
    MERGE (mobo:PlacaMae {nome: 'ASUS PRIME B550M-K'})
    SET mobo.soquete = 'AM4', mobo.chipset = 'B550', mobo.pci_express = '4.0'
    
    // 3. Cria a relação de compatibilidade entre eles
    MERGE (cpu)-[rel:COMPATIVEL_COM {requer_update_bios: true, versao_bios_minima: '2803'}]->(mobo)
    
    RETURN cpu.nome, type(rel), mobo.nome
    """
    
    with driver.session(database=NEO4J_DATABASE) as session:
        resultado = session.run(query)
        for registro in resultado:
            print(f"Sucesso! Criado: {registro['cpu.nome']} -> {registro['type(rel)']} -> {registro['mobo.nome']}")

if __name__ == "__main__":
    with get_driver() as driver:
        print("Conectando ao EvoluiPC Engine...")
        criar_setup_inicial(driver)