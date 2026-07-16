import multiprocessing
import time
import psutil
import requests
import sys

try:
    import wmi
except ImportError:
    wmi = None

API_URL = "https://evoluipc-django.onrender.com/api/machine/sync"
PING_URL = "https://evoluipc-django.onrender.com/"
TIMEOUT_PING = 60
TIMEOUT_SYNC = 60
MAX_RETRIES = 3


def ler_hardware_local():
    print("🔍 Varrendo hardware da máquina...")

    nome_cpu = "Processador não identificado"
    nome_gpu = "Não identificada"
    nome_placa_mae = "Não identificada"

    if wmi is not None:
        try:
            w = wmi.WMI()

            for cpu in w.Win32_Processor():
                nome = getattr(cpu, "Name", None)
                if nome:
                    nome_cpu = nome.strip()
                    break

            for gpu in w.Win32_VideoController():
                if getattr(gpu, "Name", None):
                    nome_gpu = gpu.Name
                    break

            for board in w.Win32_BaseBoard():
                fabricante = getattr(board, "Manufacturer", "") or ""
                produto = getattr(board, "Product", "") or ""
                nome_placa_mae = f"{fabricante} {produto}".strip() or "Não identificada"
                break
        except Exception as e:
            print(f"⚠️  Erro WMI: {e}")
    else:
        print("⚠️  WMI indisponível. CPU, GPU e placa-mãe podem não ser detectadas.")

    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3))

    return {
        "cpu": nome_cpu,
        "gpu": nome_gpu,
        "ram": f"{ram_gb}GB",
        "motherboard": nome_placa_mae,
    }


def acordar_servidor():
    print("\n📡 Conectando ao servidor (pode levar até 60s na primeira vez)...", end="", flush=True)
    try:
        inicio = time.time()
        requests.get(PING_URL, timeout=TIMEOUT_PING)
        duracao = int(time.time() - inicio)
        print(f" OK ({duracao}s)")
        return True
    except Exception:
        print(" Servidor pode estar lento, tentando enviar mesmo assim.")
        return False


def enviar_com_retry(token, meu_pc):
    payload = {
        "schema_version": "1.0",
        "source": "desktop-agent",
        "machine": meu_pc,
        "diagnostics": [
            f"CPU detectada: {meu_pc.get('cpu', 'N/A')}",
            f"GPU detectada: {meu_pc.get('gpu', 'N/A')}",
            f"RAM detectada: {meu_pc.get('ram', 'N/A')}",
            f"Placa-mãe detectada: {meu_pc.get('motherboard', 'N/A')}",
        ],
        "route": [],
        "catalog": [],
    }

    cabecalhos = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }

    for tentativa in range(1, MAX_RETRIES + 1):
        try:
            print(f"\n📤 Enviando dados... (tentativa {tentativa}/{MAX_RETRIES})")
            resposta = requests.post(API_URL, json=payload, headers=cabecalhos, timeout=TIMEOUT_SYNC)

            if resposta.status_code in [200, 201]:
                return True, None
            else:
                erro = f"Servidor recusou os dados (Código {resposta.status_code}): {resposta.text}"
                print(f"❌ {erro}")
                if resposta.status_code in [401, 403]:
                    return False, erro
        except requests.exceptions.Timeout:
            print(f"⏱️  Timeout na tentativa {tentativa}. Aguardando antes de tentar novamente...")
            time.sleep(5)
        except Exception as e:
            print(f"⚠️  Erro na tentativa {tentativa}: {e}")
            time.sleep(5)

    return False, "Número máximo de tentativas atingido."


if __name__ == "__main__":
    multiprocessing.freeze_support()

    print("=====================================")
    print("    EVOLUIPC - AGENTE DE HARDWARE    ")
    print("=====================================\n")

    usuario = input("Digite seu nome de usuário: ").strip().lower()
    token = input("Digite seu Token de Acesso (copie do painel web): ").strip()

    meu_pc = ler_hardware_local()

    print(f"\n💻 Hardware detectado:")
    print(f"   CPU:       {meu_pc['cpu']}")
    print(f"   GPU:       {meu_pc['gpu']}")
    print(f"   RAM:       {meu_pc['ram']}")
    print(f"   Placa-mãe: {meu_pc['motherboard']}")

    acordar_servidor()

    sucesso, erro = enviar_com_retry(token, meu_pc)

    print("\n=====================================")
    if sucesso:
        print(f"✅ SUCESSO! Hardware de '{usuario}' salvo na nuvem.")
    else:
        print(f"❌ FALHA ao enviar dados.")
        if erro:
            print(f"   Detalhe: {erro}")
        print("   Verifique sua conexão ou se o token está correto.")

    input("\nAperte ENTER para fechar esta janela...")