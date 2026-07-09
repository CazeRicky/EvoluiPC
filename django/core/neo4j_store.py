import os
import json
import random
from datetime import datetime, timezone
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

def get_driver():
    if not NEO4J_PASSWORD:
        raise RuntimeError("NEO4J_PASSWORD nao configurado no Django.")
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _json_dumps(value, fallback):
    try:
        return json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError):
        return json.dumps(fallback, ensure_ascii=False)


def _json_loads(value, fallback):
    if value in (None, ""):
        return fallback
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return fallback


def _user_attr(user, key, default=""):
    if isinstance(user, dict):
        return user.get(key, default)
    return getattr(user, key, default)


def get_all_cpus():
    """Busca todos os processadores disponíveis"""
    query = """
    MATCH (cpu:Processor)
    RETURN cpu.name AS name, cpu.socket AS socket, cpu.tdp AS tdp, cpu.performance_score AS performance_score
    ORDER BY cpu.name
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            results = session.run(query).data()
            return results if results else []


def get_all_gpus():
    """Busca todas as GPUs disponíveis"""
    query = """
    MATCH (gpu:Gpu)
    RETURN gpu.name AS name, gpu.interface AS interface, gpu.memory_gb AS memory_gb, gpu.power_watts AS power_watts, gpu.performance_score AS performance_score
    ORDER BY gpu.name
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            results = session.run(query).data()
            return results if results else []

def get_gpu_compatibility(gpu_name):
    query = """
    MATCH (gpu:Gpu {name: $gpu_name})-[rel:COMPATIBLE_WITH]->(mobo:Motherboard)
    RETURN gpu.name AS gpu_name, mobo.name AS motherboard_name, rel.slot_required AS slot_required, rel.pcie_version AS pcie_version
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            results = session.run(query, gpu_name=gpu_name).data()
            return results if results else []

def get_cpu_performance_score(cpu_name):
    """Busca o performance_score de um processador pelo nome"""
    query = """
    MATCH (cpu:Processor {name: $cpu_name})
    RETURN cpu.performance_score AS performance_score
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query, cpu_name=cpu_name).single()
            if result:
                return int(result["performance_score"])
            return 4000  # Default fallback


def detect_device_type(cpu_name):
    """Detecta o tipo de dispositivo baseado no nome da CPU"""
    if not cpu_name:
        return "Desktop"
    
    cpu_upper = cpu_name.upper()
    
    # Detecção de Mac (Apple Silicon)
    if "APPLE" in cpu_upper or "M1" in cpu_upper or "M2" in cpu_upper or "M3" in cpu_upper:
        return "Mac"
    
    # Detecção de Laptop (Intel móvel)
    laptop_suffixes = ["HX", "HK", "H", "P", "U", "Y", "G7", "G1"]
    for suffix in laptop_suffixes:
        if cpu_upper.endswith(suffix):
            return "Laptop"
    
    # Detecção de Laptop (AMD móvel)
    amd_laptop_suffixes = ["H", "HS", "U", "HX"]
    for suffix in amd_laptop_suffixes:
        if "RYZEN" in cpu_upper:
            for suf in amd_laptop_suffixes:
                if cpu_upper.endswith(suf):
                    return "Laptop"
    
    return "Desktop"


def get_fallback_upgrade_for_device(device_type):
    """Retorna uma recomendação de upgrade baseada no tipo de dispositivo"""
    if device_type == "Mac":
        return {
            "type": "Mac",
            "message": "Dispositivo Apple com Apple Silicon",
            "can_upgrade": False,
            "reason": "Dispositivos Mac com Apple Silicon não permitem upgrading de componentes. O processador, GPU e memória são soldados na placa-mãe. Para melhorar performance, considere um modelo mais recente de Mac."
        }
    
    if device_type == "Laptop":
        return {
            "type": "Laptop",
            "cpu": "Intel Core i7-12700H",
            "mb": "Placa-mãe Notebook",
            "score": 8500,
            "message": "Setup de Notebook para referência"
        }
    
    # Desktop
    return {
        "type": "Desktop",
        "cpu": "Intel i5-10400",
        "mb": "A320M",
        "score": 4500,
        "message": "Setup de Desktop para referência"
    }


def _extract_cpu_manufacturer(cpu_name):
    """Extrai o fabricante da CPU (Intel, AMD) baseado no nome"""
    if not cpu_name:
        return "Intel"  # Default
    cpu_upper = cpu_name.upper()
    if "AMD" in cpu_upper or "RYZEN" in cpu_upper:
        return "AMD"
    return "Intel"


def get_upgrade_recommendation(current_cpu_name, current_cpu_score):
    """
    Busca a melhor recomendação de CPU com melhor custo-benefício.
    Estratégia em 3 níveis:
    1. Buscar CPUs do MESMO FABRICANTE com score maior (melhor match)
    2. Buscar qualquer CPU Desktop com score maior
    3. Retornar vazio (será tratado como fallback no views.py)
    """
    manufacturer = _extract_cpu_manufacturer(current_cpu_name)
    
    # Tentativa 1: CPUs do mesmo fabricante com score melhor
    query_same_manufacturer = """
    MATCH (new_cpu:Processor)
    WHERE new_cpu.performance_score > $current_cpu_score 
      AND new_cpu.type = "Desktop"
      AND new_cpu.name CONTAINS $manufacturer
    WITH new_cpu, (toFloat(new_cpu.performance_score) / new_cpu.price) AS cost_benefit_ratio
    RETURN new_cpu.name AS recommendation, new_cpu.price AS price
    ORDER BY cost_benefit_ratio DESC
    LIMIT 1
    """
    
    # Tentativa 2: Qualquer CPU Desktop com score melhor
    query_generic = """
    MATCH (new_cpu:Processor)
    WHERE new_cpu.performance_score > $current_cpu_score AND new_cpu.type = "Desktop"
    WITH new_cpu, (toFloat(new_cpu.performance_score) / new_cpu.price) AS cost_benefit_ratio
    RETURN new_cpu.name AS recommendation, new_cpu.price AS price
    ORDER BY cost_benefit_ratio DESC
    LIMIT 1
    """
    
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            # Tenta primeiro com mesmo fabricante
            result = session.run(
                query_same_manufacturer,
                current_cpu_score=current_cpu_score,
                manufacturer=manufacturer,
            )
            data = result.data()
            
            # Se não encontrou, tenta qualquer CPU Desktop
            if not data:
                result = session.run(
                    query_generic,
                    current_cpu_score=current_cpu_score,
                )
                data = result.data()
            
            return data


def _estimate_gpu_score(gpu_name):
    """Gera um score aproximado para uma GPU quando o nome não está no grafo."""
    if not gpu_name:
        return 8000
    name_upper = str(gpu_name).upper()
    if "RTX 4090" in name_upper:
        return 32000
    if "RTX 4080" in name_upper:
        return 28000
    if "RTX 4070" in name_upper:
        return 24000
    if "RTX 4060" in name_upper:
        return 18000
    if "RTX 3060" in name_upper:
        return 16000
    if "RTX 2060" in name_upper:
        return 12000
    if "1660" in name_upper:
        return 9000
    if "1650" in name_upper:
        return 7000
    if "RX 7600" in name_upper:
        return 17000
    if "RX 6600" in name_upper:
        return 14000
    if "RX 570" in name_upper:
        return 8000
    return 8000


def assess_cpu_gpu_bottleneck(cpu_score, gpu_score):
    """Avalia se o processador é um gargalo para a GPU atual."""
    cpu_score = int(cpu_score or 4500)
    gpu_score = int(gpu_score or 8000)
    if gpu_score >= 24000 and cpu_score < 7000:
        return {"status": "high", "is_cpu_bottleneck": True, "reason": "Seu processador é um gargalo importante para uma placa de vídeo de alto desempenho."}
    if gpu_score >= 16000 and cpu_score < 9000:
        return {"status": "medium", "is_cpu_bottleneck": True, "reason": "Seu processador pode limitar o ganho de uma placa de vídeo mais potente."}
    return {"status": "low", "is_cpu_bottleneck": False, "reason": "Seu processador ainda pode acompanhar bem a placa de vídeo sugerida."}


def get_gpu_upgrade_recommendation(current_cpu_name, current_cpu_score, current_gpu_name=None, current_motherboard_name=None):
    """Busca uma recomendação real de GPU baseada em gargalo de CPU, compatibilidade com a placa-mãe e custo-benefício."""
    current_cpu_score = int(current_cpu_score or 4500)
    current_gpu_name = current_gpu_name or "GTX 1650"
    current_gpu_score = _estimate_gpu_score(current_gpu_name)
    bottleneck = assess_cpu_gpu_bottleneck(current_cpu_score, current_gpu_score)

    query_specific = """
    MATCH (mb:Motherboard {name: $current_motherboard_name})<-[:COMPATIBLE_WITH]-(gpu:Gpu)
    WHERE gpu.performance_score > $current_gpu_score
    WITH gpu, (toFloat(gpu.performance_score) / gpu.price) AS cost_benefit_ratio
    RETURN gpu.name AS recommendation, gpu.price AS price, gpu.performance_score AS performance_score, gpu.power_watts AS power_watts, gpu.memory_gb AS memory_gb, gpu.interface AS interface
    ORDER BY cost_benefit_ratio DESC
    LIMIT 1
    """
    query_generic = """
    MATCH (gpu:Gpu)
    WHERE gpu.performance_score > $current_gpu_score AND gpu.type = "Desktop"
    WITH gpu, (toFloat(gpu.performance_score) / gpu.price) AS cost_benefit_ratio
    RETURN gpu.name AS recommendation, gpu.price AS price, gpu.performance_score AS performance_score, gpu.power_watts AS power_watts, gpu.memory_gb AS memory_gb, gpu.interface AS interface
    ORDER BY cost_benefit_ratio DESC
    LIMIT 1
    """

    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            data = []
            if current_motherboard_name:
                result = session.run(query_specific, current_motherboard_name=current_motherboard_name, current_gpu_score=current_gpu_score)
                data = result.data()
            if not data:
                result = session.run(query_generic, current_gpu_score=current_gpu_score)
                data = result.data()
            if data:
                first = data[0]
                first["bottleneck"] = bottleneck["status"]
                first["is_cpu_bottleneck"] = bottleneck["is_cpu_bottleneck"]
                first["bottleneck_reason"] = bottleneck["reason"]
            return data


def _build_machine_payload(record):
    machine = {
        "cpu": record["cpu_name"],
        "gpu": record["gpu_name"],
        "motherboard": record["mb_name"],
        "socket": record.get("socket") or "",
        "ram_type": record.get("ram_type") or "",
        "ram": f"{random.choice([16, 32])}GB",
        "storage": random.choice(["512GB NVMe", "1TB NVMe", "1TB SATA SSD"]),
    }
    diagnostics = [
        f"CPU {machine['cpu']} compativel com {machine['motherboard']} ({machine['socket']}).",
        f"GPU selecionada: {machine['gpu']}.",
    ]
    signature = f"{machine['cpu']}|{machine['motherboard']}|{machine['gpu']}"
    return {
        "signature": signature,
        "machine": machine,
        "diagnostics": diagnostics,
    }


def get_random_pc_profile(exclude_signatures=None):
    excluded = exclude_signatures or []
    # Query simplificada: busca um processador e uma placa-mãe compatível
    query = """
    MATCH (cpu:Processor)-[:FITS_IN]->(s:Socket)<-[:HAS_SOCKET]-(mb:Motherboard)
    WHERE mb.type = "Desktop"
    WITH cpu, mb, cpu.name + '|' + mb.name AS signature
    WHERE NOT signature IN $excluded
    RETURN
      cpu.name AS cpu_name,
      coalesce(cpu.type, '') AS cpu_tier,
      coalesce(cpu.socket, '') AS socket,
      mb.name AS mb_name,
      coalesce(mb.socket, '') AS ram_type,
      "GPU Integrada" AS gpu_name,
      "Integrada" AS gpu_tier
    ORDER BY rand()
    LIMIT 1
    """
    fallback_query = """
    MATCH (cpu:Processor)-[:FITS_IN]->(s:Socket)<-[:HAS_SOCKET]-(mb:Motherboard)
    WHERE mb.type = "Desktop"
    RETURN
      cpu.name AS cpu_name,
      coalesce(cpu.type, '') AS cpu_tier,
      coalesce(cpu.socket, '') AS socket,
      mb.name AS mb_name,
      coalesce(mb.socket, '') AS ram_type,
      "GPU Integrada" AS gpu_name,
      "Integrada" AS gpu_tier
    ORDER BY rand()
    LIMIT 1
    """

    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            record = session.run(query, excluded=excluded).single()
            if not record:
                record = session.run(fallback_query).single()
            if not record:
                return None
            return _build_machine_payload(record)


def assign_random_pc_to_user(user, source="neo4j-random-assignment", exclude_signatures=None):
    profile = get_random_pc_profile(exclude_signatures=exclude_signatures)
    if not profile:
        return None

    upsert_user_pc_parts(
        user=user,
        machine=profile["machine"],
        diagnostics=profile["diagnostics"],
        source=source,
    )
    upsert_user_upgrade_options(user=user, route=[], catalog=[], source=source)
    return profile


def ensure_user_node(user):
    query = """
    MERGE (u:AppUser {user_id: $user_id})
    ON CREATE SET
      u.username = $username,
      u.email = $email,
      u.created_at = $now,
      u.updated_at = $now
    ON MATCH SET
      u.username = $username,
      u.email = $email,
      u.updated_at = $now
    RETURN u.user_id AS user_id, u.username AS username, u.email AS email, u.created_at AS created_at, u.updated_at AS updated_at
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            record = session.run(
                query,
                user_id=_user_attr(user, "id"),
                username=_user_attr(user, "username"),
                email=_user_attr(user, "email", "") or "",
                now=_now_iso(),
            ).single()
            return dict(record) if record else None


def get_user_pc_parts(user_id):
    query = """
    MATCH (u:AppUser {user_id: $user_id})
    OPTIONAL MATCH (u)-[:HAS_PC_PARTS]->(p:UserPcParts)
    RETURN properties(p) AS props
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            record = session.run(query, user_id=user_id).single()
            props = record["props"] if record else None
            if not props:
                return None

            machine_payload = props.get("machine_json", props.get("machine"))
            diagnostics_payload = props.get("diagnostics_json", props.get("diagnostics"))
            machine = _json_loads(machine_payload, {})
            machine.pop("cpu_tier", None)
            machine.pop("gpu_tier", None)
            return {
                "machine": machine,
                "diagnostics": _json_loads(diagnostics_payload, []),
                "source": props.get("source") or "neo4j",
                "collected_at": props.get("updated_at") or "",
            }


def upsert_user_pc_parts(user, machine, diagnostics, source):
    machine_clean = dict(machine)
    machine_clean.pop("cpu_tier", None)
    machine_clean.pop("gpu_tier", None)

    query = """
    MERGE (u:AppUser {user_id: $user_id})
    ON CREATE SET u.username = $username, u.email = $email, u.created_at = $now
    SET u.updated_at = $now
    
    OPTIONAL MATCH (u)-[:HAS_PC_PARTS]->(current:UserPcParts)
    WITH u, current, current.machine_json AS old_machine
    
    MERGE (u)-[:HAS_PC_PARTS]->(p:UserPcParts)
    SET p.machine_json = $machine_json,
        p.diagnostics_json = $diagnostics_json,
        p.source = $source,
        p.updated_at = $now
        
    FOREACH (ignoreMe IN CASE WHEN old_machine IS NULL OR old_machine <> $machine_json THEN [1] ELSE [] END |
        CREATE (u)-[:HAD_HARDWARE_AT {date: $now}]->(h:HardwareHistory {
            machine_json: $machine_json,
            source: $source,
            scanned_at: $now
        })
    )
    
    RETURN p.machine_json AS machine_json, p.diagnostics_json AS diagnostics_json, p.source AS source, p.updated_at AS updated_at
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            record = session.run(
                query,
                user_id=_user_attr(user, "id"),
                username=_user_attr(user, "username"),
                email=_user_attr(user, "email", "") or "",
                machine_json=_json_dumps(machine_clean, {}),
                diagnostics_json=_json_dumps(diagnostics, []),
                source=source,
                now=_now_iso(),
            ).single()
            machine_result = _json_loads(record["machine_json"], {})
            machine_result.pop("cpu_tier", None)
            machine_result.pop("gpu_tier", None)
            return {
                "machine": machine_result,
                "diagnostics": _json_loads(record["diagnostics_json"], []),
                "source": record["source"] or source,
                "collected_at": record["updated_at"] or "",
            }


def get_user_scan_history(user_id):
    query = """
    MATCH (u:AppUser {user_id: $user_id})-[:HAD_HARDWARE_AT]->(h:HardwareHistory)
    RETURN h.machine_json AS machine_json, h.scanned_at AS scanned_at
    ORDER BY h.scanned_at DESC
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            results = session.run(query, user_id=user_id).data()
            history = []
            for record in results:
                machine_data = _json_loads(record["machine_json"], {})
                history.append({
                    "scanned_at": record["scanned_at"],
                    "machine": machine_data
                })
            return history


def get_user_upgrade_options(user_id):
    query = """
    MATCH (u:AppUser {user_id: $user_id})
    OPTIONAL MATCH (u)-[:HAS_UPGRADE_OPTIONS]->(o:UserUpgradeOptions)
    RETURN properties(o) AS props
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            record = session.run(query, user_id=user_id).single()
            props = record["props"] if record else None
            if not props:
                return None

            route_payload = props.get("route_json", props.get("route"))
            catalog_payload = props.get("catalog_json", props.get("catalog"))
            return {
                "route": _json_loads(route_payload, []),
                "catalog": _json_loads(catalog_payload, []),
                "source": props.get("source") or "neo4j",
                "updated_at": props.get("updated_at") or "",
            }


def upsert_user_upgrade_options(user, route, catalog, source):
    query = """
    MERGE (u:AppUser {user_id: $user_id})
    ON CREATE SET u.username = $username, u.email = $email, u.created_at = $now
    SET u.updated_at = $now
    MERGE (u)-[:HAS_UPGRADE_OPTIONS]->(o:UserUpgradeOptions)
    SET o.route_json = $route_json,
        o.catalog_json = $catalog_json,
        o.source = $source,
        o.updated_at = $now
    RETURN o.route_json AS route_json, o.catalog_json AS catalog_json, o.source AS source, o.updated_at AS updated_at
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            record = session.run(
                query,
                user_id=_user_attr(user, "id"),
                username=_user_attr(user, "username"),
                email=_user_attr(user, "email", "") or "",
                route_json=_json_dumps(route, []),
                catalog_json=_json_dumps(catalog, []),
                source=source,
                now=_now_iso(),
            ).single()
            return {
                "route": _json_loads(record["route_json"], []),
                "catalog": _json_loads(record["catalog_json"], []),
                "source": record["source"] or source,
                "updated_at": record["updated_at"] or "",
            }


def upsert_user_profile(user, profile, source="web", event_type="generic"):
    profile_payload = profile if isinstance(profile, dict) else {"payload": profile}
    query = """
    MERGE (u:AppUser {user_id: $user_id})
    ON CREATE SET u.username = $username, u.email = $email, u.created_at = $now
    SET u.updated_at = $now
    MERGE (u)-[:HAS_PROFILE]->(p:UserProfile)
    SET p.username = $username,
        p.email = $email,
        p.profile_json = $profile_json,
        p.source = $source,
        p.event_type = $event_type,
        p.updated_at = $now
    RETURN p.profile_json AS profile_json, p.source AS source, p.event_type AS event_type, p.updated_at AS updated_at
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            record = session.run(
                query,
                user_id=_user_attr(user, "id"),
                username=_user_attr(user, "username"),
                email=_user_attr(user, "email", "") or "",
                profile_json=_json_dumps(profile_payload, {}),
                source=source,
                event_type=event_type,
                now=_now_iso(),
            ).single()
            return {
                "profile": _json_loads(record["profile_json"], {}),
                "source": record["source"] or source,
                "event_type": record["event_type"] or event_type,
                "updated_at": record["updated_at"] or "",
            }


def get_user_profile(user_id):
    query = """
    MATCH (u:AppUser {user_id: $user_id})
    OPTIONAL MATCH (u)-[:HAS_PROFILE]->(p:UserProfile)
    RETURN properties(p) AS props
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            record = session.run(query, user_id=user_id).single()
            props = record["props"] if record else None
            if not props:
                return None
            profile_payload = props.get("profile_json", props.get("profile"))
            return {
                "profile": _json_loads(profile_payload, {}),
                "source": props.get("source") or "neo4j",
                "event_type": props.get("event_type") or "generic",
                "updated_at": props.get("updated_at") or "",
            }


def upsert_device_classification(user, cpu_classification, source="device-scanner"):
    """
    Armazena a classificação do dispositivo (Desktop/Laptop) para o usuário.
    
    cpu_classification deve ser um dicionário com:
    - device_type: "Desktop" ou "Laptop"
    - cpu_suffix: sufixo do processador (ex: "K", "H", "HX")
    - description: descrição do sufixo
    - confidence: confiança da classificação (0-100)
    """
    query = """
    MERGE (u:AppUser {user_id: $user_id})
    ON CREATE SET u.username = $username, u.email = $email, u.created_at = $now
    SET u.updated_at = $now
    MERGE (u)-[:HAS_DEVICE_INFO]->(d:DeviceClassification)
    SET d.device_type = $device_type,
        d.cpu_suffix = $cpu_suffix,
        d.description = $description,
        d.confidence = $confidence,
        d.source = $source,
        d.detected_at = $now
    RETURN d.device_type AS device_type, d.cpu_suffix AS cpu_suffix, d.confidence AS confidence
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            record = session.run(
                query,
                user_id=_user_attr(user, "id"),
                username=_user_attr(user, "username"),
                email=_user_attr(user, "email", "") or "",
                device_type=cpu_classification.get("device_type", "Desconhecido"),
                cpu_suffix=cpu_classification.get("cpu_suffix", ""),
                description=cpu_classification.get("description", ""),
                confidence=cpu_classification.get("confidence", 0),
                source=source,
                now=_now_iso(),
            ).single()
            return {
                "device_type": record["device_type"],
                "cpu_suffix": record["cpu_suffix"],
                "confidence": record["confidence"],
            }