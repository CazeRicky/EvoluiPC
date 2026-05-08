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

def buscar_gpus(driver):
    """Busca todas as GPUs no banco"""
    query = """
    MATCH (gpu:GPU)
    RETURN gpu.nome, gpu.arquitetura, gpu.vram, gpu.tdp, gpu.performance
    ORDER BY gpu.nome
    """
    
    with driver.session(database=NEO4J_DATABASE) as session:
        resultado = session.run(query)
        gpus = [dict(registro) for registro in resultado]
        return gpus

def buscar_compatibilidade_gpu(driver, gpu_nome: str):
    """Busca compatibilidades de uma GPU específica (ex: slot PCIe)"""
    query = """
    MATCH (gpu:GPU {nome: $gpu_nome})-[rel:COMPATIVEL_COM]->(mobo:PlacaMae)
    RETURN gpu.nome, mobo.nome, mobo.pci_express, rel.slot_requerido
    """
    
    with driver.session(database=NEO4J_DATABASE) as session:
        resultado = session.run(query, gpu_nome=gpu_nome)
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

def criar_setup_gpus(driver):
    """Cria dados iniciais de GPUs"""
    query = """
    // 1. Cria as GPUs
    MERGE (gpu1:GPU {nome: 'RTX 4080'})
    SET gpu1.arquitetura = 'Ada', gpu1.vram = 16, gpu1.tdp = 320, gpu1.performance = 18000
    WITH gpu1
    
    // 2. Cria a segunda GPU
    MERGE (gpu2:GPU {nome: 'RTX 4070'})
    SET gpu2.arquitetura = 'Ada', gpu2.vram = 12, gpu2.tdp = 200, gpu2.performance = 12000
    WITH gpu1, gpu2
    
    // 3. Busca a placa-mãe existente
    MATCH (mobo:PlacaMae {nome: 'ASUS PRIME B550M-K'})
    
    // 4. Cria compatibilidades entre GPUs e placa-mãe
    MERGE (gpu1)-[rel1:COMPATIVEL_COM {slot_requerido: 'PCIe_x16', versao_minima: '4.0'}]->(mobo)
    MERGE (gpu2)-[rel2:COMPATIVEL_COM {slot_requerido: 'PCIe_x16', versao_minima: '4.0'}]->(mobo)
    
    RETURN gpu1.nome, gpu2.nome, mobo.nome
    """
    
    with driver.session(database=NEO4J_DATABASE) as session:
        resultado = session.run(query)
        for registro in resultado:
            print(f"Sucesso! Criadas GPUs: {registro['gpu1.nome']}, {registro['gpu2.nome']} -> compatíveis com {registro['mobo.nome']}")

if __name__ == "__main__":
    with get_driver() as driver:
        print("Conectando ao EvoluiPC Engine...")
        
        # 1. Criar dados iniciais (seed)
        print("\n[1] Criando dados iniciais de CPU...")
        criar_setup_inicial(driver)
        
        # 2. Criar dados de GPU
        print("\n[2] Criando dados iniciais de GPU...")
        criar_setup_gpus(driver)
        
        # 3. Buscar processadores existentes
        print("\n[3] Buscando processadores disponíveis...")
        cpus = buscar_processadores(driver)
        for cpu in cpus:
            print(f"  - {cpu['cpu.nome']} (Socket: {cpu['cpu.soquete']}, TDP: {cpu['cpu.tdp']}W, Performance: {cpu['cpu.performance']})")
        
        # 4. Buscar GPUs existentes
        print("\n[4] Buscando GPUs disponíveis...")
        gpus = buscar_gpus(driver)
        for gpu in gpus:
            print(f"  - {gpu['gpu.nome']} (Arquitetura: {gpu['gpu.arquitetura']}, VRAM: {gpu['gpu.vram']}GB, TDP: {gpu['gpu.tdp']}W, Performance: {gpu['gpu.performance']})")
        
        # 5. Buscar compatibilidades CPU
        print("\n[5] Buscando compatibilidades de CPU...")
        compatibilidades_cpu = buscar_compatibilidade(driver, "Ryzen 7 5700X3D")
        for comp in compatibilidades_cpu:
            print(f"  - {comp['cpu.nome']} é compatível com {comp['mobo.nome']} (Chipset: {comp['mobo.chipset']})")
        
        # 6. Buscar compatibilidades GPU
        print("\n[6] Buscando compatibilidades de GPU...")
        compatibilidades_gpu = buscar_compatibilidade_gpu(driver, "RTX 4080")
        for comp in compatibilidades_gpu:
            print(f"  - {comp['gpu.nome']} é compatível com {comp['mobo.nome']} (PCIe {comp['mobo.pci_express']}, slot: {comp['rel.slot_requerido']})")