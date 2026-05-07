from neo4j_config import NEO4J_DATABASE, get_driver

def buscar_processadores(driver):
    """Busca todos os processadores no banco"""
    query = """
    MATCH (cpu:Processador)
    RETURN cpu.nome, cpu.soquete, cpu.tdp, cpu.performance
    ORDER BY cpu.nome
    """
    
    with driver.session(database=NEO4J_DATABASE) as session:
        resultado = session.run(query)
        processadores = [dict(registro) for registro in resultado]
        return processadores

def buscar_compatibilidade(driver, cpu_nome: str):
    """Busca placas-mãe compatíveis com um processador específico"""
    query = """
    MATCH (cpu:Processador {nome: $cpu_nome})-[rel:COMPATIVEL_COM]->(mobo:PlacaMae)
    RETURN cpu.nome, mobo.nome, mobo.chipset, rel.requer_update_bios, rel.versao_bios_minima
    """
    
    with driver.session(database=NEO4J_DATABASE) as session:
        resultado = session.run(query, cpu_nome=cpu_nome)
        compatibilidades = [dict(registro) for registro in resultado]
        return compatibilidades

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
        
        # 1. Criar dados iniciais (seed)
        print("\n[1] Criando dados iniciais...")
        criar_setup_inicial(driver)
        
        # 2. Buscar processadores existentes
        print("\n[2] Buscando processadores disponíveis...")
        cpus = buscar_processadores(driver)
        for cpu in cpus:
            print(f"  - {cpu['cpu.nome']} (Socket: {cpu['cpu.soquete']}, TDP: {cpu['cpu.tdp']}W)")
        
        # 3. Buscar compatibilidades
        print("\n[3] Buscando compatibilidades...")
        compatibilidades = buscar_compatibilidade(driver, "Ryzen 7 5700X3D")
        for comp in compatibilidades:
            print(f"  - {comp['cpu.nome']} é compatível com {comp['mobo.nome']} (Chipset: {comp['mobo.chipset']})")