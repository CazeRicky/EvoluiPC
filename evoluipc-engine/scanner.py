import psutil
import cpuinfo
import wmi
import requests
import multiprocessing

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
    maquina = {
        "cpu": nome_cpu,
        "gpu": nome_gpu,
        "ram": ram_str,
        "motherboard": nome_placa_mae
    }
    
    return maquina

if __name__ == "__main__":
    multiprocessing.freeze_support()
    print("=====================================")
    print("    EVOLUIPC - AGENTE DE HARDWARE    ")
    print("=====================================\n")
    
    # Pergunta quem é o usuário
    usuario = input("Digite seu nome de usuário do site EvoluiPC: ")
    
    # Roda a leitura
    meu_pc = ler_hardware_local()
    
    print("\n Máquina Detectada:")
    for peca, detalhe in meu_pc.items():
        print(f"- {peca.upper()}: {detalhe}")
        
    print("\n📡 Tentando enviar dados para o servidor EvoluiPC...")
    
    payload = {
        "username": usuario,
        "hardware": meu_pc
    }
    
    try:
        # Tenta enviar para a nossa API local
        resposta = requests.post("http://127.0.0.1:8000/api/machine/upload", json=payload)
        
        if resposta.status_code == 200:
            print(" Sucesso! Servidor recebeu os dados. Pode olhar o site.")
        else:
            print(f" Erro no servidor: código {resposta.status_code}")
    except Exception as e:
        print("Erro: Não foi possível conectar ao servidor. (O Uvicorn está desligado no momento)")