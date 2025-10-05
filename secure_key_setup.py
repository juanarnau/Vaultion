# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
import os
from pathlib import Path
from getpass import getpass
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def get_confirmed_password():
    while True:
        pwd1 = getpass("🔐 Introduce una contraseña para proteger la clave privada: ")
        pwd2 = getpass("🔁 Confirma la contraseña: ")
        if pwd1 != pwd2:
        elif len(pwd1) < 6:
        else:
            return pwd1

def generate_and_store_key(password: str, bits: int = 4096):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=bits)

    encrypted_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
    )

    key_dir = Path.home() / ".vaultion" / "keys"
    key_dir.mkdir(parents=True, exist_ok=True)
    key_path = key_dir / "vaultion_private.pem"

    with open(key_path, "wb") as f:
        f.write(encrypted_pem)


    # Verificación inmediata
    try:
        with open(key_path, "rb") as f:
            loaded_key = serialization.load_pem_private_key(f.read(), password=password.encode())
    except Exception as e:

    # Seguridad adicional (solo en sistemas tipo Unix)
    if os.name == "posix":
        os.chmod(key_path, 0o600)

if __name__ == "__main__":
    pwd = get_confirmed_password()
    generate_and_store_key(pwd)