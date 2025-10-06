# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau

import sys
import uuid
import json
from pathlib import Path
from PySide6.QtWidgets import QMessageBox
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
import psutil

# 📁 Rutas internas
VAULTION_HOME = Path.home() / ".vaultion"
VAULTION_HOME.mkdir(parents=True, exist_ok=True)
DB_PATH = VAULTION_HOME / "vaultion.db"
LOCAL_KEY_PATH = VAULTION_HOME / "vaultion.key"

# 🔍 Detectar USB dinámicamente
def detect_usb_key():
    for part in psutil.disk_partitions():
        if "removable" in part.opts.lower():
            key_path = Path(part.mountpoint) / "vaultion.key"
            if key_path.exists() or key_path.parent.exists():
                return key_path
    return None

# 🔐 Validar estructura de clave
def validate_key(key_path: Path) -> bool:
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

# 🧬 Crear nueva clave
def generate_new_key(target_path: Path) -> Path:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    message = str(uuid.uuid4())
    signature = private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    key_data = {
        "message": message,
        "signature": signature.hex(),
        "public_key": public_pem
    }

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(key_data, f, indent=2)

    return target_path

# ✅ Verificar firma (opcional en tu flujo)
def verify_signature_and_authorization(message, signature_hex, public_key_pem) -> bool:
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
    except Exception:
        return False

# 🚀 Inicializar Vaultion
def boot_vaultion() -> Path:
    key_path = detect_usb_key()

    if key_path is None:
        QMessageBox.critical(None, "USB no detectado", "Conecta un USB para continuar.")
        sys.exit(1)

    if not key_path.exists():
        reply = QMessageBox.question(
            None,
            "Clave no encontrada",
            f"No se encontró una clave en el USB ({key_path}).\n¿Deseas crear una nueva?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            return generate_new_key(key_path)
        else:
            sys.exit(0)

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
                QMessageBox.critical(None, "Error", f"No se pudo eliminar la clave:\n{e}")
                sys.exit(1)
            return generate_new_key(key_path)
        else:
            sys.exit(0)

    return key_path

# 📁 Ruta de base de datos
def get_database_path() -> Path:
    key_path = detect_usb_key()
    if not validate_key(key_path):
        raise RuntimeError("Clave inválida detectada en get_database_path()")
    return DB_PATH

# 📦 Cargar datos de clave
def load_key_data(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# 📂 Obtener raíz del USB
def get_usb_root() -> Path | None:
    key_file = boot_vaultion()
    if key_file:
        return key_file.parent
    return None

if __name__ == "__main__":
    boot_vaultion()