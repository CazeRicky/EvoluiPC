import binascii
import hashlib
import hmac
import os
import uuid
from dataclasses import dataclass

from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from .neo4j_store import NEO4J_DATABASE, get_driver


@dataclass
class Neo4jUser:
    id: str
    username: str
    email: str = ""

    @property
    def is_authenticated(self):
        return True


def _now_iso():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def _new_token():
    return str(uuid.uuid4())


def _new_user_id():
    return str(uuid.uuid4())


def _hash_password(password, salt_hex):
    salt = binascii.unhexlify(salt_hex)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 390000)
    return binascii.hexlify(digest).decode("ascii")


def _password_record(password):
    salt_hex = binascii.hexlify(os.urandom(16)).decode("ascii")
    return {
        "salt": salt_hex,
        "hash": _hash_password(password, salt_hex),
    }


def _run_one(query, **params):
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            return session.run(query, **params).single()


def _run_all(query, **params):
    with get_driver() as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            return list(session.run(query, **params))


def _issue_token_for_user(user_id):
    token = _new_token()
    query = """
    MATCH (u:AppUser {user_id: $user_id})
    OPTIONAL MATCH (u)-[:HAS_TOKEN]->(old:AuthToken)
    WITH u, collect(old) AS olds
    FOREACH (old IN olds | DETACH DELETE old)
    CREATE (t:AuthToken {value: $token, created_at: $now, updated_at: $now})
    CREATE (u)-[:HAS_TOKEN]->(t)
    RETURN t.value AS token
    """
    record = _run_one(query, user_id=user_id, token=token, now=_now_iso())
    return record["token"] if record else token


def ensure_user_identity(username, email, password):
    duplicate = _run_one(
        """
        MATCH (u:AppUser)
        WHERE u.username = $username OR ($email <> '' AND u.email = $email)
        RETURN u.user_id AS user_id
        LIMIT 1
        """,
        username=username,
        email=email or "",
    )
    if duplicate:
        raise ValueError("Usuario ou email ja cadastrado.")

    user_id = _new_user_id()
    password_data = _password_record(password)
    token = _new_token()
    query = """
    CREATE (u:AppUser {
      user_id: $user_id,
      username: $username,
      email: $email,
      password_salt: $password_salt,
      password_hash: $password_hash,
      created_at: $now,
      updated_at: $now
    })
    CREATE (t:AuthToken {value: $token, created_at: $now, updated_at: $now})
    CREATE (u)-[:HAS_TOKEN]->(t)
    RETURN u.user_id AS user_id, u.username AS username, u.email AS email, t.value AS token
    """
    record = _run_one(
        query,
        user_id=user_id,
        username=username,
        email=email or "",
        password_salt=password_data["salt"],
        password_hash=password_data["hash"],
        token=token,
        now=_now_iso(),
    )
    if not record:
        raise RuntimeError("Falha ao criar usuario no Neo4j.")
    return {
        "id": record["user_id"],
        "username": record["username"],
        "email": record["email"],
        "token": record["token"],
    }


def authenticate_identity(username, password):
    record = _run_one(
        """
        MATCH (u:AppUser {username: $username})
        RETURN u.user_id AS user_id, u.username AS username, u.email AS email, u.password_salt AS password_salt, u.password_hash AS password_hash
        LIMIT 1
        """,
        username=username,
    )
    if not record:
        return None

    expected_hash = _hash_password(password, record["password_salt"])
    if not hmac.compare_digest(expected_hash, record["password_hash"]):
        return None

    token = _issue_token_for_user(record["user_id"])
    return {
        "id": record["user_id"],
        "username": record["username"],
        "email": record["email"],
        "token": token,
    }


def get_user_by_token(token):
    record = _run_one(
        """
        MATCH (t:AuthToken {value: $token})<-[:HAS_TOKEN]-(u:AppUser)
        RETURN u.user_id AS user_id, u.username AS username, u.email AS email, t.value AS token
        LIMIT 1
        """,
        token=token,
    )
    if not record:
        return None
    return {
        "id": record["user_id"],
        "username": record["username"],
        "email": record["email"],
        "token": record["token"],
    }


def revoke_token(token):
    _run_all(
        """
        MATCH (t:AuthToken {value: $token})
        DETACH DELETE t
        """,
        token=token,
    )


class Neo4jTokenAuthentication(BaseAuthentication):
    keyword = "Token"

    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if not header:
            return None

        if header[0].decode("utf-8") != self.keyword:
            return None

        if len(header) != 2:
            raise AuthenticationFailed("Cabecalho Token invalido.")

        token = header[1].decode("utf-8")
        user = get_user_by_token(token)
        if not user:
                        raise AuthenticationFailed("Token invalido ou expirado.")

        return Neo4jUser(id=user["id"], username=user["username"], email=user["email"]), token