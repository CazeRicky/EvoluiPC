import psutil
import cpuinfo
import wmi
import requests
import multiprocessing
from cpu_classifier import classificar_dispositivo


DJANGO_API_BASE = "http://127.0.0.1:8000"

def ler_hardware_local():
    print("Iniciando varredura profunda de hardware...")
    
    # 1. Lê o Processador (CPU)
    info_cpu = cpuinfo.get_cpu_info()
    nome_cpu = info_cpu.get('brand_raw', 'Processador não identificado')

    # 2. Lê a Memória RAM
    ram_bytes = psutil.virtual_memory().total
    ram_gb = round(ram_bytes / (1024 ** 3)) # Converte de Bytes para Gigabytes
    ram_str = f"{ram_gb}GB"

    # 3. Inicia o WMI para ler GPU e Placa-mãe
    nome_gpu = "Não identificada"
    nome_placa_mae = "Não identificada"
    
    try:
        w = wmi.WMI()
        
        # Pega a Placa de Vídeo
        for gpu in w.Win32_VideoController():
            nome_gpu = gpu.Name
            break # Pega a principal e para

        # Pega a Placa-mãe
        for board in w.Win32_BaseBoard():
            nome_placa_mae = f"{board.Manufacturer} {board.Product}"
            break
            
    except Exception as e:
        print(f"⚠️ Erro ao ler dados da placa (WMI): {e}")

    # Monta o pacote de dados
    classificacao_cpu = classificar_dispositivo(nome_cpu)
    
    maquina = {
        "cpu": nome_cpu,
        "gpu": nome_gpu,
        "ram": ram_str,
        "motherboard": nome_placa_mae,
        "device_type": classificacao_cpu['device_type'],
        "cpu_suffix": classificacao_cpu['cpu_suffix'],
        "cpu_classification": {
            "type": classificacao_cpu['device_type'],
            "suffix": classificacao_cpu['cpu_suffix'],
            "description": classificacao_cpu['description'],
            "confidence": classificacao_cpu['confidence']
        }
    }
    
    return maquina

if __name__ == "__main__":
    multiprocessing.freeze_support()
    print("=====================================")
    print("    EVOLUIPC - AGENTE DE HARDWARE    ")
    print("=====================================\n")
    
    # Pede credenciais para associar o hardware a uma conta existente.
    usuario = input("Digite seu nome de usuário do site EvoluiPC: ").strip()
    senha = input("Digite sua senha do site EvoluiPC: ").strip()
    
    # Roda a leitura
    meu_pc = ler_hardware_local()
    
    print("\n 📱 Máquina Detectada:")
    for peca, detalhe in meu_pc.items():
        if peca == "cpu_classification":
            continue  # Pula a exibição do dicionário completo
        print(f"- {peca.upper()}: {detalhe}")
    
    # Exibe a classificação
    classificacao = meu_pc.get('cpu_classification', {})
    if classificacao:
        tipo = classificacao.get('type', 'Desconhecido')
        sufixo = classificacao.get('suffix', 'N/A')
        conf = classificacao.get('confidence', 0)
        print(f"\n🔍 Classificação de Dispositivo:")
        print(f"- Tipo: {tipo}")
        print(f"- Sufixo CPU: {sufixo if sufixo else '(não identificado)'}")
        print(f"- Confiança: {conf}%")
        print(f"- Descrição: {classificacao.get('description', 'N/A')}")
        
    print("\n📡 Autenticando no servidor EvoluiPC...")
    
    try:
        login_response = requests.post(
            f"{DJANGO_API_BASE}/api/auth/login",
            json={"username": usuario, "password": senha},
            timeout=15,
        )

        if login_response.status_code != 200:
            print(f" Erro ao autenticar: código {login_response.status_code}")
            print(login_response.text)
            raise SystemExit(1)

        login_data = login_response.json()
        token = login_data.get("token")
        if not token:
            print(" Erro: autenticação sem token retornado.")
            raise SystemExit(1)

        print("✅ Autenticado. Enviando hardware para o banco...")

        payload = {
            "schema_version": "1.0",
            "machine": meu_pc,
            "diagnostics": [
                f"Dispositivo classificado como {meu_pc.get('device_type', 'Desconhecido')}",
                f"Sufixo detectado: {meu_pc.get('cpu_suffix') or 'nenhum'}",
            ],
            "route": [],
            "catalog": [],
            "source": "desktop-agent",
        }

        resposta = requests.post(
            f"{DJANGO_API_BASE}/api/machine/sync",
            json=payload,
            headers={"Authorization": f"Token {token}"},
            timeout=15,
        )

        if resposta.status_code == 200:
            print("✅ Sucesso! O hardware foi salvo no banco e já deve aparecer no sistema web.")
        else:
            print(f" Erro no servidor: código {resposta.status_code}")
            print(resposta.text)
    except Exception as e:
        print("Erro: Não foi possível conectar ao servidor. (O Uvicorn está desligado no momento)")
        print(str(e))