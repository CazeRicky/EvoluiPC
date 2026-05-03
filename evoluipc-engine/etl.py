import csv
import json
import os

def limpar_preco(valor_str):
    if not valor_str or str(valor_str).strip() == "":
        return 0.0
    limpo = str(valor_str).replace('$', '').replace(',', '').strip()
    try:
        return float(limpo)
    except ValueError:
        return 0.0

def simplificar_soquete(socket_string):
    if not socket_string:
        return "Desconhecido"
    s = str(socket_string).upper()
    if "AM4" in s: return "AM4"
    if "AM5" in s: return "AM5"
    if "LGA1151" in s or "1151" in s: return "LGA1151"
    if "LGA1200" in s or "1200" in s: return "LGA1200"
    if "LGA1700" in s or "1700" in s: return "LGA1700"
    if "AM3" in s: return "AM3"
    return str(socket_string).split('/')[0].strip()

def rodar_etl():
    print("Iniciando conversão CSV -> JSON...")
    hardware_limpo = {"processadores": [], "placas_de_video": [], "placas_mae": []}

    # 1. CPUs
    try:
        with open('cpus_github.csv', mode='r', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                nome = linha.get('CpuName', linha.get('name', ''))
                nome = nome.split('-')[0].strip() if '-' in nome else nome
                soquete = simplificar_soquete(linha.get('Socket', linha.get('socket', '')))
                preco = limpar_preco(linha.get('Price at introduction', linha.get('price', '0')))
                if nome and soquete != "Desconhecido":
                    hardware_limpo["processadores"].append({
                        "nome": nome, "soquete": soquete, "tier": "Mid", "preco": preco if preco > 0 else 500
                    })
        print(f"✅ {len(hardware_limpo['processadores'])} CPUs processadas.")
    except Exception as e: print(f"⚠️ Erro nas CPUs: {e}")

    # 2. GPUs
    try:
        with open('gpus_github.csv', mode='r', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                nome = linha.get('gpuName', linha.get('name', ''))
                preco = limpar_preco(linha.get('price', '0'))
                pts = linha.get('G3Dmark', '0')
                pontos = int(pts) if str(pts).isdigit() else 0
                if nome:
                    tier = "Low"
                    if pontos > 10000: tier = "Mid"
                    if pontos > 18000: tier = "High"
                    if pontos > 25000: tier = "Ultra"
                    hardware_limpo["placas_de_video"].append({
                        "nome": nome, "tier": tier, "preco": preco if preco > 0 else 1000
                    })
        print(f"✅ {len(hardware_limpo['placas_de_video'])} GPUs processadas.")
    except Exception as e: print(f"⚠️ Erro nas GPUs: {e}")

    # 3. Placas-Mãe
    try:
        with open('mobos_github.csv', mode='r', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                nome = linha.get('name', '')
                soquete = simplificar_soquete(linha.get('socket', ''))
                preco = limpar_preco(linha.get('price', '0'))
                ram_tipo = "DDR5" if "DDR5" in str(linha.get('memory_type', '')).upper() else "DDR4"
                if nome and soquete != "Desconhecido":
                    hardware_limpo["placas_mae"].append({
                        "nome": nome, "soquete": soquete, "ram_tipo": ram_tipo, "preco": preco if preco > 0 else 600
                    })
        print(f"✅ {len(hardware_limpo['placas_mae'])} Placas-mãe processadas.")
    except Exception as e:
        print("⚠️ Erro nas Mobos. Injetando modelos genéricos por segurança...")
        hardware_limpo["placas_mae"].extend([
            {"nome": "A320M Genérica", "soquete": "AM4", "ram_tipo": "DDR4", "preco": 350},
            {"nome": "B550M Avançada", "soquete": "AM4", "ram_tipo": "DDR4", "preco": 800},
            {"nome": "B650M Nova Geração", "soquete": "AM5", "ram_tipo": "DDR5", "preco": 1300},
            {"nome": "H610M Padrão", "soquete": "LGA1700", "ram_tipo": "DDR4", "preco": 600}
        ])

    with open('hardware.json', 'w', encoding='utf-8') as f:
        json.dump(hardware_limpo, f, indent=4, ensure_ascii=False)
    print("🚀 ETL Concluído! hardware.json gerado.")

if __name__ == "__main__":
    rodar_etl()