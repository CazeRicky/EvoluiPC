import multiprocessing
import psutil
import cpuinfo
import requests
import sys

try:
    import wmi
except ImportError:
    wmi = None


API_URL = "https://evoluipc-django.onrender.com/api/machine/sync"


def ler_hardware_local():
    print("Iniciando varredura profunda de hardware...")

    info_cpu = cpuinfo.get_cpu_info()
    nome_cpu = info_cpu.get("brand_raw", "Processador não identificado")
    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3))

    nome_gpu = "Não identificada"
    nome_placa_mae = "Não identificada"

    if wmi is not None:
        try:
            w = wmi.WMI()

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
            print(f"⚠️ Erro WMI: {e}")
    else:
        print("⚠️ Biblioteca WMI não disponível. GPU e placa-mãe podem não ser detectadas.")

    return {
        "cpu": nome_cpu,
        "gpu": nome_gpu,
        "ram": f"{ram_gb}GB",
        "motherboard": nome_placa_mae
    }


def montar_payload(meu_pc):
    return {
        "schema_version": "1.0",
        "source": "desktop-agent",
        "machine": meu_pc,
        "diagnostics": [
            f"CPU detectada: {meu_pc.get('cpu', 'N/A')}",
            f"GPU detectada: {meu_pc.get('gpu', 'N/A')}",
            f"RAM detectada: {meu_pc.get('ram', 'N/A')}",
            f"Placa-mãe detectada: {meu_pc.get('motherboard', 'N/A')}"
        ],
        "route": [],
        "catalog": []
    }


def enviar_para_servidor(token, payload):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }

    response = requests.post(
        API_URL,
        json=payload,
        headers=headers,
        timeout=20
    )
    return response


if __name__ == "__main__":
    multiprocessing.freeze_support()

    print("=====================================")
    print("    EVOLUIPC - AGENTE DE HARDWARE    ")
    print("=====================================\n")

    usuario = input("Digite seu nome de usuário: ").strip().lower()
    token = input("Cole seu token de autenticação: ").strip()

    if not usuario:
        print("\n❌ Usuário não informado.")
        input("Aperte ENTER para fechar esta janela...")
        sys.exit(1)

    if not token:
        print("\n❌ Token não informado.")
        input("Aperte ENTER para fechar esta janela...")
        sys.exit(1)

    meu_pc = ler_hardware_local()
    payload = montar_payload(meu_pc)

    print("\n📦 Dados coletados:")
    print(f"- Usuário informado: {usuario}")
    print(f"- CPU: {meu_pc['cpu']}")
    print(f"- GPU: {meu_pc['gpu']}")
    print(f"- RAM: {meu_pc['ram']}")
    print(f"- Placa-mãe: {meu_pc['motherboard']}")

    print("\n📡 Enviando para o servidor EvoluiPC...")

    try:
        resposta = enviar_para_servidor(token, payload)

        if resposta.status_code == 200:
            print(f"\n✅ SUCESSO! Dados enviados com sucesso para '{usuario}'.")
            try:
                data = resposta.json()
                print("\n📄 Resposta do servidor:")
                print(data)
            except Exception:
                print("\n📄 Resposta textual do servidor:")
                print(resposta.text)

        elif resposta.status_code == 401:
            print("\n❌ ERRO 401: Token inválido ou expirado.")
            print("Verifique se você colou o token correto retornado pelo login.")

        elif resposta.status_code == 403:
            print("\n❌ ERRO 403: Acesso negado.")
            print("O servidor recebeu a requisição, mas recusou a autorização.")

        elif resposta.status_code == 404:
            print("\n❌ ERRO 404: Endpoint não encontrado.")
            print(f"Verifique a rota configurada: {API_URL}")

        else:
            print(f"\n❌ ERRO NO SERVIDOR: Código {resposta.status_code}")
            print(f"URL tentada: {API_URL}")
            print(f"Resposta: {resposta.text}")

    except requests.exceptions.Timeout:
        print("\n❌ ERRO: Tempo limite excedido ao tentar conectar ao servidor.")
        print("O backend pode estar demorando para responder ou pode estar indisponível.")

    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ ERRO DE CONEXÃO: {e}")
        print("Verifique se a URL do backend está correta e se o serviço está online no Render.")

    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")

    print("\n=====================================")
    input("Aperte ENTER para fechar esta janela...")