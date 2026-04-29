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
    query = """
    MATCH (cpu:Processador)-[:COMPATIVEL_COM]->(mb:PlacaMae)
    MATCH (gpu:PlacaDeVideo)
    WITH cpu, mb, gpu, cpu.nome + '|' + mb.nome + '|' + gpu.nome AS signature
    WHERE NOT signature IN $excluded
    RETURN
      cpu.nome AS cpu_name,
      coalesce(cpu.tier, '') AS cpu_tier,
      coalesce(cpu.soquete, '') AS socket,
      mb.nome AS mb_name,
      coalesce(mb.ram_tipo, '') AS ram_type,
      gpu.nome AS gpu_name,
      coalesce(gpu.tier, '') AS gpu_tier
    ORDER BY rand()
    LIMIT 1
    """
    fallback_query = """
    MATCH (cpu:Processador)-[:COMPATIVEL_COM]->(mb:PlacaMae)
    MATCH (gpu:PlacaDeVideo)
    RETURN
      cpu.nome AS cpu_name,
      coalesce(cpu.tier, '') AS cpu_tier,
      coalesce(cpu.soquete, '') AS socket,
      mb.nome AS mb_name,
      coalesce(mb.ram_tipo, '') AS ram_type,
      gpu.nome AS gpu_name,
      coalesce(gpu.tier, '') AS gpu_tier
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
    MERGE (u)-[:HAS_PC_PARTS]->(p:UserPcParts)
    SET p.machine_json = $machine_json,
        p.diagnostics_json = $diagnostics_json,
        p.source = $source,
        p.updated_at = $now
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


def get_device_classification(user_id):
    """Recupera a classificação do dispositivo para um usuário"""
    query = """
    MATCH (u:AppUser {user_id: $user_id})
    OPTIONAL MATCH (u)-[:HAS_DEVICE_INFO]->(d:DeviceClassification)
    RETURN properties(d) AS props
    """
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            record = session.run(query, user_id=user_id).single()
            props = record["props"] if record else None
            if not props:
                return None
            return {
                "device_type": props.get("device_type", "Desconhecido"),
                "cpu_suffix": props.get("cpu_suffix", ""),
                "description": props.get("description", ""),
                "confidence": props.get("confidence", 0),
                "detected_at": props.get("detected_at", ""),
            }
