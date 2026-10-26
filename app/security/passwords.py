"""Hash e verificação de senhas com scrypt (stdlib), sem senhas em texto puro."""
import base64
import hashlib
import hmac
import secrets

_N, _R, _P = 2**14, 8, 1
_SALT_BYTES = 16


def _derive(password: str, salt: bytes) -> bytes:
    """Deriva a chave scrypt da senha com o salt informado."""
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=_N, r=_R, p=_P, dklen=32)


def hash_password(password: str) -> str:
    """Gera o hash `scrypt$salt$digest` (base64) de uma senha, com salt aleatório."""
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = _derive(password, salt)
    return "scrypt${}${}".format(
        base64.b64encode(salt).decode(), base64.b64encode(digest).decode()
    )


def verify_password(password: str, stored_hash: str) -> bool:
    """Confere a senha contra o hash armazenado em tempo constante."""
    try:
        scheme, salt_b64, digest_b64 = stored_hash.split("$")
        if scheme != "scrypt":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)
    except ValueError:
        return False
    return hmac.compare_digest(_derive(password, salt), expected)


# Hash descartável para equalizar o tempo de resposta quando o usuário não existe
# (evita enumeração de usuários por timing).
DUMMY_HASH: str = hash_password(secrets.token_urlsafe(16))
