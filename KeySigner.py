from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

SIGNING_KEY_PATH = Path("vaultion_signing.pem")

def generate_signing_key():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with open(SIGNING_KEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    return private_key

def sign_key(private_key, key_bytes: bytes) -> bytes:
    return private_key.sign(
        key_bytes,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32),
        hashes.SHA256()
    )

def verify_signature(public_key, key_bytes: bytes, signature: bytes) -> bool:
    try:
        public_key.verify(
            signature,
            key_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False