# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
import os
from pathlib import Path
import json
import platform
import psutil
from PySide6.QtWidgets import QMessageBox
import sys
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import json
import uuid

VAULTION_HOME = Path.home() / ".vaultion"
VAULTION_HOME.mkdir(parents=True, exist_ok=True)
DB_PATH = VAULTION_HOME / "vaultion.db"
LOCAL_KEY_PATH = Path.home() / ".vaultion" / "vaultion.key"

def get_active_key_path():
    usb_key = detect_usb_key()
    if usb_key and usb_key.exists():
        return usb_key
    return None  # No fallback a clave local

def find_usb_key_file():
    # Detecta unidades extraíbles (Windows)
    from win32api import GetLogicalDriveStrings
    from win32file import GetDriveType, DRIVE_REMOVABLE

    drives = GetLogicalDriveStrings().split('\000')[:-1]
    for drive in drives:
        if GetDriveType(drive) == DRIVE_REMOVABLE:
            key_path = Path(drive) / "vaultion.key"
            if key_path.exists():
                return key_path
    return None

def load_key_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def verify_signature_and_authorization(message, signature_hex, public_key_pem):
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.exceptions import InvalidSignature

    try:
        pubkey = serialization.load_pem_public_key(public_key_pem.encode())
        pubkey.verify(
            bytes.fromhex(signature_hex),
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        return False

def boot_vaultion():
    key_path = get_active_key_path()

    if not key_path:
        QMessageBox.critical(None, "USB no detectado", "Conecta el USB con la clave Vaultion para continuar.")
        sys.exit(1)

    if not key_path.exists():
        return generate_new_key(key_path)

    if not validate_key(key_path):
        reply = QMessageBox.question(
            None,
            "Clave inválida",
            f"La clave en el USB ({key_path}) no es válida.\n¿Deseas eliminarla y generar una nueva?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                key_path.unlink()
            except Exception as e:
                sys.exit(1)
            return generate_new_key(key_path)
        else:
            sys.exit(0)

    return key_path

def get_database_path():
    key_path = get_active_key_path()
    if not validate_key(key_path):
        raise RuntimeError("Clave inválida detectada en get_database_path()")
    return Path.home() / ".vaultion" / "vaultion.db"

def get_usb_root():
    key_file = boot_vaultion()
    if key_file:
        return Path(key_file).parent
    return None

def detect_usb_path():
    from pathlib import Path
    import psutil
    for part in psutil.disk_partitions():
        if "removable" in part.opts:
            return Path(part.mountpoint)
    return None


def create_new_key(path: Path):
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import serialization, hashes
    import json

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    message = "USB_ID"
    signature = key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    payload = {
        "message": message,
        "signature": signature.hex(),  # ← guardamos como texto hexadecimal
        "public_key": public_key
    }

    with open(path, "w") as f:
        json.dump(payload, f, indent=4)


def validate_key(key_path):
    try:
        with open(key_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return all([
            isinstance(data.get("message"), str) and data["message"].strip(),
            isinstance(data.get("signature"), str) and data["signature"].strip(),
            isinstance(data.get("public_key"), str) and data["public_key"].strip()
        ])
    except Exception:
        return False

def generate_new_key(target_path):
    # 1. Crear clave privada RSA
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # 2. Extraer clave pública
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    # 3. Crear mensaje único (puede ser UUID, ID de USB, etc.)
    message = str(uuid.uuid4()).encode("utf-8")

    # 4. Firmar el mensaje
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # 5. Guardar clave en formato Vaultion
    key_data = {
        "message": message.decode("utf-8"),
        "signature": signature.hex(),
        "public_key": public_pem
    }

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(key_data, f, indent=2)

    return target_path

def boot_vaultion():
    key_path = get_active_key_path()

    if key_path is None:
        QMessageBox.critical(None, "USB no detectado", "Conecta el USB con la clave Vaultion para continuar.")
        sys.exit(1)

    if not key_path.exists():
        return generate_new_key(key_path)

    if not validate_key(key_path):
        reply = QMessageBox.question(
            None,
            "Clave inválida",
            f"La clave en el USB ({key_path}) no es válida.\n¿Deseas eliminarla y generar una nueva?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                key_path.unlink()
            except Exception as e:
                sys.exit(1)
            return generate_new_key(key_path)
        else:
            sys.exit(0)

    return key_path

def detect_usb_key():
    # Devuelve la ruta de vaultion.key si está en un USB
    for drive in Path("D:/"), Path("E:/"), Path("F:/"):  # puedes hacer esto dinámico
        key = drive / "vaultion.key"
        if key.exists():
            return key
    return None

if __name__ == "__main__":
    boot_vaultion()