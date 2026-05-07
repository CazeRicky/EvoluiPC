"""
Classificador de CPU para determinar se é Desktop ou Laptop
Baseado nas nomenclaturas oficiais da Intel e AMD
"""
import re


# Sufixos Intel - Desktop
INTEL_DESKTOP_SUFFIXES = {
    'K': 'Alto desempenho, desbloqueado',
    'KF': 'Alto desempenho desbloqueado, requer gráficos discretos',
    'F': 'Requer gráficos discretos',
    'S': 'Edição especial',
    'T': 'Estilo de vida com otimização do consumo de energia',
}

# Sufixos Intel - Laptop/Móvel
INTEL_MOBILE_SUFFIXES = {
    'HX': 'Desempenho mais alto, todas as UNs desbloqueadas',
    'HK': 'Desempenho mais alto, todas as UNs desbloqueadas',
    'H': 'Desempenho máximo',
    'P': 'Desempenho otimizado para notebooks finos e leves',
    'U': 'Eficiente em termos de energia',
    'Y': 'Extremamente eficiente em termos de baixo consumo de energia',
    'G7': 'Nível gráfico (processador móvel com tecnologia gráfica)',
    'G1': 'Nível gráfico (processador móvel com tecnologia gráfica)',
}

# Sufixos AMD - Desktop
AMD_DESKTOP_SUFFIXES = {
    'X': 'Alta performance',
    'XT': 'Performance superior e clocks maiores que o "X"',
    'X3D': 'Tecnologia AMD 3D V-Cache (foco em jogos)',
    'G': 'Possui placa de vídeo integrada (APU)',
    'GE': 'Baixo consumo de energia com vídeo integrado',
}

# Sufixos AMD - Laptop/Móvel
AMD_MOBILE_SUFFIXES = {
    'H': 'Alta performance (notebooks gamers/profissionais)',
    'HS': 'Alta performance com melhor eficiência energética',
    'U': 'Foco em baixo consumo (notebooks finos/ultraportáteis)',
    'HX': 'Performance extrema (notebooks de altíssimo desempenho)',
}


def extrair_sufixo_cpu(nome_cpu: str) -> tuple[str, str, str]:
    """
    Extrai o sufixo do processador e classifica como Desktop ou Laptop.
    
    Retorna: (sufixo, tipo_dispositivo, descricao)
    - sufixo: string com o sufixo encontrado (ex: 'K', 'H', 'XT')
    - tipo_dispositivo: 'Desktop' ou 'Laptop' ou 'Desconhecido'
    - descricao: descrição do sufixo
    """
    if not nome_cpu:
        return '', 'Desconhecido', 'CPU não identificada'
    
    nome_cpu = nome_cpu.strip().upper()
    
    # Tenta encontrar sufixos Intel primeiro (mais específico para mobile)
    # Procura por padrões como: "i7-13700H", "i5-12500K", etc
    for sufixo in sorted(INTEL_MOBILE_SUFFIXES.keys(), key=len, reverse=True):
        if nome_cpu.endswith(sufixo):
            return sufixo, 'Laptop', INTEL_MOBILE_SUFFIXES[sufixo]
    
    for sufixo in sorted(INTEL_DESKTOP_SUFFIXES.keys(), key=len, reverse=True):
        if nome_cpu.endswith(sufixo):
            return sufixo, 'Desktop', INTEL_DESKTOP_SUFFIXES[sufixo]
    
    # Tenta encontrar sufixos AMD
    for sufixo in sorted(AMD_MOBILE_SUFFIXES.keys(), key=len, reverse=True):
        if nome_cpu.endswith(sufixo):
            return sufixo, 'Laptop', AMD_MOBILE_SUFFIXES[sufixo]
    
    for sufixo in sorted(AMD_DESKTOP_SUFFIXES.keys(), key=len, reverse=True):
        if nome_cpu.endswith(sufixo):
            return sufixo, 'Desktop', AMD_DESKTOP_SUFFIXES[sufixo]

    # Se o nome termina em número, sem letra final, a tendência é ser desktop.
    # Isso cobre casos como "Intel Core i5-13600" e "AMD Ryzen 5 7600".
    if re.search(r"\d$", nome_cpu):
        if 'INTEL' in nome_cpu and 'CORE' in nome_cpu:
            return '', 'Desktop', 'Processador Intel Core sem sufixo identificável, provável desktop'
        if 'AMD' in nome_cpu and 'RYZEN' in nome_cpu:
            return '', 'Desktop', 'Processador AMD Ryzen sem sufixo identificável, provável desktop'
    
    # Se não encontrou sufixo conhecido, tenta heurística
    if 'INTEL' in nome_cpu and 'CORE' in nome_cpu:
        # Intel Core com sufixo não identificado, mas sem indicação móvel
        return '', 'Desktop', 'Processador Intel Core (sufixo não identificado, provável desktop)'
    elif 'AMD' in nome_cpu and 'RYZEN' in nome_cpu:
        # AMD Ryzen com sufixo não identificado, mas sem indicação móvel
        return '', 'Desktop', 'Processador AMD Ryzen (sufixo não identificado, provável desktop)'
    
    return '', 'Desconhecido', 'Processador não classificado'


def classificar_dispositivo(nome_cpu: str) -> dict:
    """
    Classifica o dispositivo como Desktop ou Laptop com base no nome do CPU.
    
    Retorna um dicionário com:
    - cpu_suffix: sufixo extraído
    - device_type: 'Desktop' ou 'Laptop'
    - description: descrição detalhada
    - confidence: nível de confiança da classificação (0-100)
    """
    sufixo, tipo, descricao = extrair_sufixo_cpu(nome_cpu)
    
    # Define confiança baseado se encontrou sufixo conhecido
    confianca = 100 if sufixo else 50
    
    return {
        'cpu_suffix': sufixo,
        'device_type': tipo,
        'description': descricao,
        'confidence': confianca
    }


def obter_lista_sufixos() -> dict:
    """
    Retorna um dicionário com todos os sufixos conhecidos e suas categorias.
    Útil para fins informativos e validação.
    """
    return {
        'intel_desktop': INTEL_DESKTOP_SUFFIXES,
        'intel_mobile': INTEL_MOBILE_SUFFIXES,
        'amd_desktop': AMD_DESKTOP_SUFFIXES,
        'amd_mobile': AMD_MOBILE_SUFFIXES,
    }


if __name__ == "__main__":
    # Testes
    exemplos = [
        "Intel Core i7-13700K",
        "Intel Core i9-13900HX",
        "AMD Ryzen 7 7700X",
        "AMD Ryzen 5 7600H",
        "Intel Core i5-12500",
        "AMD Ryzen 9 7950X3D",
    ]
    
    print("🔍 Teste de Classificação de CPU\n")
    for cpu in exemplos:
        resultado = classificar_dispositivo(cpu)
        print(f"CPU: {cpu}")
        print(f"  └─ Tipo: {resultado['device_type']} | Sufixo: {resultado['cpu_suffix']} | Confiança: {resultado['confidence']}%")
        print(f"  └─ Descrição: {resultado['description']}\n")
