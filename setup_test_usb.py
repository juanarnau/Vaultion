import json
import base64
import datetime
from pathlib import Path
from getpass import getpass
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.exceptions import InvalidSignature
from authorized_keys_manager import add_key

# Ruta segura de la clave privada
PRIVATE_KEY_PATH = Path.home() / ".vaultion" / "keys" / "vaultion_private.pem"

def detect_usb_drive():
    try:
        from win32api import GetLogicalDriveStrings
        from win32file import GetDriveType, DRIVE_REMOVABLE

        drives = GetLogicalDriveStrings().split('\000')[:-1]
        for drive in drives:
            if GetDriveType(drive) == DRIVE_REMOVABLE:
                return Path(drive)
    except Exception as e:
        print(f"⚠️ Error al detectar USB: {e}")
    return None

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

def setup_usb():
    print("🔍 Buscando USB...")
    usb_path = detect_usb_drive()
    if not usb_path:
        print("❌ No se detectó ningún USB conectado.")
        return

    print(f"📁 USB detectado en: {usb_path}")
    alias = input("📝 Alias para esta clave (ej. VaultionTestKey): ").strip()
    usb_id = input("🔢 Identificador único del USB (ej. USB_ID_TEST_001): ").strip()

    try:
        private_key = load_private_key(PRIVATE_KEY_PATH)
    except Exception as e:
        print(f"❌ Error al cargar la clave privada: {e}")
        return

    message = generate_message(usb_id)
    signature = sign_message(message, private_key)
    public_key = export_public_key(private_key)

    key_data = {
        "message": message,
        "signature": signature,
        "public_key": public_key,
        "alias": alias
    }

    save_key_file(usb_path, key_data)
    add_key(alias, public_key, usb_id)
    print("🎉 USB registrado y autorizado correctamente.")

if __name__ == "__main__":
    setup_usb()