import psutil
import cpuinfo
import wmi
import requests
import multiprocessing
import sys

def ler_hardware_local():
    print("Iniciando varredura profunda de hardware...")
    info_cpu = cpuinfo.get_cpu_info()
    nome_cpu = info_cpu.get('brand_raw', 'Processador não identificado')
    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3))
    
    nome_gpu = "Não identificada"
    nome_placa_mae = "Não identificada"
    try:
        w = wmi.WMI()
        for gpu in w.Win32_VideoController():
            nome_gpu = gpu.Name
            break
        for board in w.Win32_BaseBoard():
            nome_placa_mae = f"{board.Manufacturer} {board.Product}"
            break
    except Exception as e:
        print(f"⚠️ Erro WMI: {e}")

    return {
        "cpu": nome_cpu,
        "gpu": nome_gpu,
        "ram": f"{ram_gb}GB",
        "motherboard": nome_placa_mae
    }

if __name__ == "__main__":
    multiprocessing.freeze_support()
    print("=====================================")
    print("    EVOLUIPC - AGENTE DE HARDWARE    ")
    print("=====================================\n")
    
    usuario = input("Digite seu nome de usuário: ").strip().lower()
    token = input("Digite seu Token de Acesso (copie do painel web): ").strip()
    
    meu_pc = ler_hardware_local()
    
    payload = {
        "username": usuario,
        "machine": meu_pc
    }
    
    cabecalhos = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Se der erro 404, tente tirar o "/api" e deixar apenas "/machine/sync"
        url = "https://evoluipc-django.onrender.com/api/machine/sync"
        
        print(f"\n📡 Apresentando credenciais e enviando dados para a nuvem...")
        resposta = requests.post(url, json=payload, headers=cabecalhos, timeout=15)
        
        if resposta.status_code in [200, 201]:
            print(f"\n✅ SUCESSO! Dados de hardware salvos na nuvem para o usuário '{usuario}'.")
        else:
            print(f"\n❌ ERRO NO SERVIDOR: O servidor recusou os dados (Código {resposta.status_code})")
            print(f"Resposta do servidor: {resposta.text}")
            
    except Exception as e:
        print(f"\n❌ ERRO DE CONEXÃO: Não foi possível alcançar o servidor.")
        print(f"Detalhe técnico: {e}")
        print("Verifique sua conexão com a internet ou se o servidor do EvoluiPC está online.")

    print("\n=====================================")
    input("Aperte ENTER para fechar esta janela...")