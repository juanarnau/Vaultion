# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
import json
import base64
import datetime
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from getpass import getpass

# Ruta donde está la clave privada del usuario
PRIVATE_KEY_PATH = "vaultion_private.pem"

from getpass import getpass
from cryptography.hazmat.primitives import serialization

def load_private_key(path):
    with open(path, "rb") as f:
        pem_data = f.read()
    password = getpass("🔐 Introduce la contraseña de la clave privada: ")
    return serialization.load_pem_private_key(pem_data, password=password.encode())

def generate_message(usb_id: str) -> str:
    timestamp = datetime.datetime.utcnow().isoformat()
    return f"{usb_id}|{timestamp}"

def sign_message(message: str, private_key) -> str:
    signature = private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()

def export_public_key(private_key) -> str:
    public_key = private_key.public_key()
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

def save_key_file(usb_path: Path, key_data: dict):
    key_file = usb_path / "vaultion.key"
    with open(key_file, "w", encoding="utf-8") as f:
        json.dump(key_data, f, indent=2)
    print(f"✅ Clave guardada en: {key_file}")

def register_usb(usb_path: str, usb_id: str, alias: str):
    private_key = load_private_key(PRIVATE_KEY_PATH)
    message = generate_message(usb_id)
    signature = sign_message(message, private_key)
    public_key = export_public_key(private_key)

    key_data = {
        "message": message,
        "signature": signature,
        "public_key": public_key,
        "alias": alias
    }

    save_key_file(Path(usb_path), key_data)

# Ejemplo de uso
if __name__ == "__main__":
    # Reemplaza con la ruta real del USB y su ID
    register_usb("D:/", "USB_ID_1234567890", "VaultionKey1")