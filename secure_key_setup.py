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
            print("❌ Las contraseñas no coinciden. Intenta de nuevo.\n")
        elif len(pwd1) < 6:
            print("⚠️ Usa al menos 6 caracteres para mayor seguridad.\n")
        else:
            return pwd1

def generate_and_store_key(password: str, bits: int = 4096):
    print("🔧 Generando clave privada RSA...")
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

    print(f"✅ Clave guardada en: {key_path}")

    # Verificación inmediata
    try:
        with open(key_path, "rb") as f:
            loaded_key = serialization.load_pem_private_key(f.read(), password=password.encode())
        print("🔐 Verificación exitosa: la clave puede descifrarse con la contraseña.")
    except Exception as e:
        print(f"❌ Error al verificar la clave: {e}")

    # Seguridad adicional (solo en sistemas tipo Unix)
    if os.name == "posix":
        os.chmod(key_path, 0o600)
        print("🔒 Permisos ajustados: solo lectura/escritura para el propietario.")

if __name__ == "__main__":
    pwd = get_confirmed_password()
    generate_and_store_key(pwd)