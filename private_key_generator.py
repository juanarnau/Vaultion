# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path

def generate_private_key(password: str = None, bits: int = 2048):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits
    )

    encryption = serialization.BestAvailableEncryption(password.encode()) if password else serialization.NoEncryption()

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption
    )

    key_path = Path("vaultion_private.pem")
    with open(key_path, "wb") as f:
        f.write(pem)

    print(f"✅ Clave privada generada y guardada en: {key_path.resolve()}")

# Ejemplo de uso
if __name__ == "__main__":
    # Puedes dejar la contraseña en blanco si no quieres cifrarla
    generate_private_key(password="MiClaveSegura123", bits=4096)