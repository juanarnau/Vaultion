from pathlib import Path
import os
import secrets

KEY_PATH = Path("D:/vaultion.key")  # ⚠️ Ajusta según la letra real del USB

# 🔐 Generar nueva clave y guardarla en el USB
def generate_key():
    key = secrets.token_bytes(32)  # 256 bits
    with open(KEY_PATH, "wb") as f:
        f.write(key)
    print(f"✅ Clave generada y guardada en: {KEY_PATH}")
    return key

# 📥 Cargar clave existente desde el USB
def load_key():
    if not KEY_PATH.exists():
        print("❌ No se encontró vaultion.key en el USB.")
        return None
    with open(KEY_PATH, "rb") as f:
        key = f.read()
    print("🔑 Clave cargada correctamente.")
    return key

# 🧪 Verificar longitud y formato
def validate_key(key: bytes):
    return isinstance(key, bytes) and len(key) == 32