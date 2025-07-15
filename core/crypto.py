import base64
import os
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

VAULT_FILE = "data/vault.enc"


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend(),
    )
    return kdf.derive(password.encode())


def encrypt_data(data: list, password: str) -> bytes:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    json_data = json.dumps(data).encode()
    encrypted = aesgcm.encrypt(nonce, json_data, None)
    return base64.b64encode(salt + nonce + encrypted)


def decrypt_data(encrypted_b64: bytes, password: str) -> list:
    raw = base64.b64decode(encrypted_b64)
    salt = raw[:16]
    nonce = raw[16:28]
    ciphertext = raw[28:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    decrypted = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(decrypted)


def save_vault(data: list, password: str):
    enc = encrypt_data(data, password)
    with open(VAULT_FILE, "wb") as f:
        f.write(enc)


def load_vault(password: str) -> list:
    if not os.path.exists(VAULT_FILE):
        return []
    try:
        with open(VAULT_FILE, "rb") as f:
            enc = f.read()
        return decrypt_data(enc, password)
    except Exception as e:
        print("❌ خطا در بارگذاری vault:", e)
        return []
