# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
import json
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from authorized_keys_manager import is_key_authorized

def load_key_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def verify_signature(message: str, signature_b64: str, public_key_pem: str) -> bool:
    try:
        signature = base64.b64decode(signature_b64)
        public_key = serialization.load_pem_public_key(public_key_pem.encode())

        public_key.verify(
            signature,
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        print(f"Error al verificar la firma: {e}")
        return False

def verify_signature_and_authorization(message: str, signature_b64: str, public_key_pem: str) -> bool:
    if not is_key_authorized(public_key_pem):
        print("❌ Clave no autorizada. USB rechazado.")
        return False

    try:
        signature = base64.b64decode(signature_b64)
        public_key = serialization.load_pem_public_key(public_key_pem.encode())

        public_key.verify(
            signature,
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print("✅ Firma válida y clave autorizada.")
        return True
    except InvalidSignature:
        print("❌ Firma inválida.")
        return False
    except Exception as e:
        print(f"⚠️ Error en la verificación: {e}")
        return False
