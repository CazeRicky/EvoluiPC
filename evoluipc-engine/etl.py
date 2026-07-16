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


def _primeiro_valor(linha, *chaves):
    """Retorna o primeiro valor não vazio dentre várias colunas possíveis.
    Permite aceitar CSVs de fontes diferentes sem reescrever o ETL."""
    for chave in chaves:
        valor = linha.get(chave)
        if valor not in (None, ""):
            return valor
    return ""

_MICROARQUITETURA_PARA_SOQUETE = {
    # AMD
    "zen 5": "AM5",
    "zen 4": "AM5",
    "zen 3": "AM4",
    "zen 3+": "AM4",
    "zen 2": "AM4",
    "zen+": "AM4",
    "zen": "AM4",
    # Intel
    "arrow lake": "LGA1851",
    "raptor lake": "LGA1700",
    "raptor lake refresh": "LGA1700",
    "alder lake": "LGA1700",
    "rocket lake": "LGA1200",
    "comet lake": "LGA1200",
    "coffee lake": "LGA1151",
    "coffee lake refresh": "LGA1151",
    "kaby lake": "LGA1151",
    "skylake": "LGA1151",
}


def _soquete_por_microarquitetura(microarquitetura):
    if not microarquitetura:
        return ""
    chave = str(microarquitetura).strip().lower()
    return _MICROARQUITETURA_PARA_SOQUETE.get(chave, "")


def rodar_etl():
    print("Iniciando conversão CSV -> JSON...")
    hardware_limpo = {"processadores": [], "placas_de_video": [], "placas_mae": []}

    try:
        with open('cpus_github.csv', mode='r', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                nome = _primeiro_valor(linha, 'CpuName', 'name', 'Name')
                nome = nome.split('-')[0].strip() if '-' in nome else nome
                soquete_bruto = _primeiro_valor(linha, 'Socket', 'socket')
                if not soquete_bruto:
                    soquete_bruto = _soquete_por_microarquitetura(
                        _primeiro_valor(linha, 'microarchitecture')
                    )
                soquete = simplificar_soquete(soquete_bruto)
                preco = limpar_preco(_primeiro_valor(linha, 'Price at introduction', 'price', 'Price'))
                if nome and soquete != "Desconhecido":
                    hardware_limpo["processadores"].append({
                        "nome": nome, "soquete": soquete, "tier": "Mid", "preco": preco if preco > 0 else 500
                    })
        print(f"✅ {len(hardware_limpo['processadores'])} CPUs processadas.")
    except Exception as e:
        print(f"⚠️ Erro nas CPUs: {e}")

    try:
        with open('gpus_github.csv', mode='r', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                nome = _primeiro_valor(linha, 'gpuName', 'name', 'chipset', 'Name')
                preco = limpar_preco(_primeiro_valor(linha, 'price', 'Price'))
                pts = _primeiro_valor(linha, 'G3Dmark', 'benchmark')
                pontos = int(pts) if str(pts).isdigit() else 0
                if nome:
                    if pontos > 0:
                        tier = "Low"
                        if pontos > 10000: tier = "Mid"
                        if pontos > 18000: tier = "High"
                        if pontos > 25000: tier = "Ultra"
                    else:
                        # Sem benchmark disponível (ex.: docyx não traz G3Dmark),
                        # usa o preço como proxy aproximado de tier.
                        tier = "Low"
                        if preco > 1500: tier = "Mid"
                        if preco > 3000: tier = "High"
                        if preco > 6000: tier = "Ultra"
                    hardware_limpo["placas_de_video"].append({
                        "nome": nome, "tier": tier, "preco": preco if preco > 0 else 1000
                    })
        print(f"✅ {len(hardware_limpo['placas_de_video'])} GPUs processadas.")
    except Exception as e:
        print(f"⚠️ Erro nas GPUs: {e}")

    try:
        with open('mobos_github.csv', mode='r', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                nome = _primeiro_valor(linha, 'name', 'Name')
                soquete = simplificar_soquete(_primeiro_valor(linha, 'socket', 'Socket'))
                preco = limpar_preco(_primeiro_valor(linha, 'price', 'Price'))
                ram_tipo_raw = _primeiro_valor(linha, 'memory_type', 'ram_type')
                ram_tipo = "DDR5" if "DDR5" in str(ram_tipo_raw).upper() else "DDR4"
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