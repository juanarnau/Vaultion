# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
from pathlib import Path
import os
import secrets

KEY_PATH = Path("D:/vaultion.key")  # ⚠️ Ajusta según la letra real del USB

# 🔐 Generar nueva clave y guardarla en el USB
def generate_key():
    key = secrets.token_bytes(32)  # 256 bits
    with open(KEY_PATH, "wb") as f:
        f.write(key)
    return key

# 📥 Cargar clave existente desde el USB
def load_key():
    if not KEY_PATH.exists():
        return None
    with open(KEY_PATH, "rb") as f:
        key = f.read()
    return key

# 🧪 Verificar longitud y formato
def validate_key(key: bytes):
    return isinstance(key, bytes) and len(key) == 32