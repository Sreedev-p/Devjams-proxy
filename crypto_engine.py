import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

MASTER_SECRET = os.getenv("DATAEXPIRY_MASTER_SECRET", "hackathon_fallback_secret_36h").encode()
hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'dataexpiry-kek-context')
KEK = hkdf.derive(MASTER_SECRET)
kek_gcm = AESGCM(KEK)

def generate_dek() -> bytes:
    return os.urandom(32)

def wrap_dek(dek: bytes) -> tuple[bytes, bytes]:
    nonce = os.urandom(12)
    return kek_gcm.encrypt(nonce, dek, associated_data=None), nonce

def unwrap_dek(encrypted_dek: bytes, nonce: bytes) -> bytes:
    return kek_gcm.decrypt(nonce, encrypted_dek, associated_data=None)

def encrypt_payload(plaintext: str, dek: bytes) -> tuple[str, str]:
    gcm = AESGCM(dek)
    nonce = os.urandom(12)
    ciphertext = gcm.encrypt(nonce, plaintext.encode('utf-8'), associated_data=None)
    return base64.b64encode(nonce).decode('utf-8'), base64.b64encode(ciphertext).decode('utf-8')

def decrypt_payload(b64_ciphertext: str, b64_nonce: str, dek: bytes) -> str:
    gcm = AESGCM(dek)
    return gcm.decrypt(base64.b64decode(b64_nonce), base64.b64decode(b64_ciphertext), associated_data=None).decode('utf-8')
