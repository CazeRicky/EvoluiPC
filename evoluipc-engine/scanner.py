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
    meu_pc = ler_hardware_local()
    
    print(f"\n📡 Enviando para o servidor...")
    
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
        url = "http://127.0.0.1:8002/api/machine/upload"
        resposta = requests.post(url, json=payload, timeout=10)
        
        if resposta.status_code == 200:
            print(f"\n✅ SUCESSO! Dados enviados para '{usuario}'.")
        else:
            print(f"\n❌ ERRO NO SERVIDOR: Código {resposta.status_code}")
            print(f"Caminho tentado: {url}")
            print(f"Resposta: {resposta.text}")
            
    except Exception as e:
        print(f"\n❌ ERRO DE CONEXÃO: {e}")
        print("Verifique se o Docker está rodando e a porta 8002 está aberta.")

    print("\n=====================================")
    input("Aperte ENTER para fechar esta janela...")
