# src/app/core/security.py
from __future__ import annotations
import os, hmac, hashlib

_ALGO = "pbkdf2"
_ITER = 310_000
_SALT_BYTES = 16
_KEY_LEN = 32

def _pbkdf2(password: str, salt: bytes, iterations: int = _ITER) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=_KEY_LEN)

def hash_password(password: str) -> str:
    salt = os.urandom(_SALT_BYTES)
    digest = _pbkdf2(password, salt, _ITER)
    return f"{_ALGO}${_ITER}${salt.hex()}${digest.hex()}"

def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iter_s, salt_hex, hash_hex = stored.split("$", 3)
        if algo != _ALGO:
            return False
        iters = int(iter_s)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        candidate = _pbkdf2(password, salt, iters)
        return hmac.compare_digest(candidate, expected)
    except Exception:
        return False