# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
import sqlite3
from pathlib import Path
from datetime import datetime
import shutil
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from vaultion_boot import get_database_path

# 📁 Configuración
SALT = b"vaultion_salt_001"
VAULTION_HOME = Path.home() / ".vaultion"
VAULTION_HOME.mkdir(parents=True, exist_ok=True)
DB_PATH = VAULTION_HOME / "vaultion.db"

# 🔐 Derivar clave AES desde clave maestra
def derive_key(secret: bytes, salt: bytes = SALT) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000
    )
    return kdf.derive(secret)

# 🔐 Cifrar texto plano con AES-EAX
def encrypt_data(key: bytes, plaintext: str) -> bytes:
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    return cipher.nonce + tag + ciphertext

# 🔓 Descifrar datos con AES-EAX
def decrypt_data(key: bytes, encrypted: bytes) -> str:
    if not isinstance(encrypted, bytes):
        raise TypeError(f"❌ encrypted no es bytes, es {type(encrypted)}")
    if len(encrypted) < 32:
        raise ValueError("❌ Añade la contraseña y una nota necesaria.")

    nonce = encrypted[:16]
    tag = encrypted[16:32]
    ciphertext = encrypted[32:]

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()

# 💾 Añadir entrada cifrada
def add_entry(key: bytes, service: str, username: str, password: str, notes: str = "", owner_id: str = "default"):
    try:
        encrypted_pw = encrypt_data(key, password)
        if not notes or notes.strip() == "":
            notes = " "  # 🧷 Valor mínimo para evitar errores de descifrado
        encrypted_notes = encrypt_data(key, notes) if notes else b""
        now = datetime.utcnow().isoformat()

        assert isinstance(encrypted_pw, bytes), "encrypted_pw no es tipo bytes"
        assert isinstance(encrypted_notes, bytes), "encrypted_notes no es tipo bytes"

        conn = sqlite3.connect(get_database_path())
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                username TEXT NOT NULL,
                encrypted_password BLOB NOT NULL,
                encrypted_notes BLOB,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                owner_id TEXT NOT NULL
            )
        """)

        cursor.execute("""
            INSERT INTO vault_entries (
                service, username, encrypted_password, encrypted_notes,
                created_at, updated_at, owner_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            service, username, encrypted_pw, encrypted_notes,
            now, now, owner_id
        ))

        conn.commit()

    except Exception as e:
        pass
    finally:
        conn.close()

def sanitize_blob(blob):
    return bytes(blob) if not isinstance(blob, bytes) else blob

def safe_decrypt(blob, key: bytes) -> str:
    if not blob:
        return ""
    if not isinstance(blob, (bytes, bytearray)):
        return ""
    if len(blob) < 32:
        return ""
    try:
        return decrypt_data(key, blob)
    except Exception as e:
        return "❌ Error"

# 📖 Leer entradas
def get_entries(key: bytes, owner_id: str = "default"):
    conn = sqlite3.connect(get_database_path())
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, service, username, encrypted_password, encrypted_notes, created_at
        FROM vault_entries
        WHERE owner_id = ?
        ORDER BY created_at DESC
    """, (owner_id,))
    rows = cursor.fetchall()
    conn.close()

    entries = []
    for row in rows:
        entry_id = row[0]
        service = row[1]
        username = row[2]
        pw_blob = row[3]
        notes_blob = row[4]
        created_at = row[5]
        # 🧼 Sanitizar blobs cifrados
        pw_blob = sanitize_blob(row[3])
        notes_blob = sanitize_blob(row[4]) if row[4] else b""

        # 🔍 Inspección visual antes de descifrar
        inspect_encrypted_entry(entry_id, pw_blob, notes_blob)

        # 🧼 Reconversión si no son bytes
        if not isinstance(pw_blob, bytes):
            pw_blob = sanitize_blob(row[3])

        if notes_blob and not isinstance(notes_blob, bytes):
            notes_blob = row[4]  # sin sanitizar, lo maneja safe_decrypt
        # 🔓 Descifrado seguro
        try:

            decrypted_pw = decrypt_data(key, pw_blob)
            decrypted_notes = safe_decrypt(notes_blob, key)

        except Exception as e:
            decrypted_pw = "❌ Error"
            decrypted_notes = "❌ Error"

        entries.append({
            "id": entry_id,
            "service": service,
            "username": username,
            "encrypted_password": pw_blob,
            "encrypted_notes": notes_blob,
            "created_at": created_at,
            "password": decrypted_pw,
            "notes": decrypted_notes
        })

    return entries

def repair_empty_notes_entries(db_path: str, key: bytes):
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, encrypted_notes FROM entries")
    entries = cursor.fetchall()

    repaired = 0
    for entry_id, blob in entries:
        if not blob or not isinstance(blob, (bytes, bytearray)) or len(blob) < 32:
            fixed_blob = encrypt_data(key, "-")
            cursor.execute("UPDATE entries SET encrypted_notes = ? WHERE id = ?", (fixed_blob, entry_id))
            repaired += 1

    conn.commit()
    conn.close()

# 🔄 Actualizar entrada
def update_entry(entry_id, service, username, password, notes, key):
    encrypted_password = encrypt_data(key, password)
    if not notes or notes.strip() == "":
        notes = " "  # 🧷 Valor mínimo para evitar errores de descifrado
    encrypted_notes = encrypt_data(key, notes)

    conn = sqlite3.connect(get_database_path())
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE vault_entries
        SET service = ?, username = ?, encrypted_password = ?, encrypted_notes = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (service, username, encrypted_password, encrypted_notes, entry_id))
    conn.commit()
    conn.close()

def sanitize_blob(blob):
    if isinstance(blob, memoryview):
        return blob.tobytes()
    if isinstance(blob, str):
        return bytes(blob, 'latin1')
    if not isinstance(blob, bytes):
        return bytes(blob)
    return blob

# 🗑️ Eliminar entrada
def delete_entry(entry_id: int):
    conn = sqlite3.connect(get_database_path())
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vault_entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

# 🔍 Verificar existencia
def entry_exists(service: str, username: str) -> bool:
    conn = sqlite3.connect(get_database_path())
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vault_entries WHERE service=? AND username=?", (service, username))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def decrypt_field(blob: bytes, key: bytes) -> str:
    return decrypt_data(key, blob)

# 🔄 Rotar clave maestra
def rotate_master_key(old_key: bytes, new_key: bytes):
    conn = sqlite3.connect(get_database_path())
    cursor = conn.cursor()
    cursor.execute("SELECT id, encrypted_password, encrypted_notes FROM vault_entries")
    rows = cursor.fetchall()

    for row in rows:
        entry_id = row[0]
        old_pw = decrypt_data(old_key, row[1])
        old_notes = decrypt_data(old_key, row[2]) if row[2] else ""

        new_pw = encrypt_data(new_key, old_pw)
        new_notes = encrypt_data(new_key, old_notes)

        cursor.execute("""
            UPDATE vault_entries
            SET encrypted_password = ?, encrypted_notes = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (new_pw, new_notes, entry_id))

    conn.commit()
    conn.close()

# 🧯 Copia de seguridad
def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = VAULTION_HOME / f"vaultion_backup_{timestamp}.db"
    shutil.copy(DB_PATH, backup_path)

def inspect_encrypted_entry(entry_id: int, encrypted_pw: bytes, encrypted_notes: bytes = b""):

    def inspect_blob(label: str, blob: bytes):

        if not isinstance(blob, bytes):
            return

        if len(blob) < 32:
            return

        nonce = blob[:16]
        tag = blob[16:32]
        ciphertext = blob[32:]


    inspect_blob("Contraseña cifrada", encrypted_pw)
    if encrypted_notes:
        inspect_blob("Notas cifradas", encrypted_notes)
    else:
        pass


# 🧱 Inicializar base de datos
def initialize_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ✅ Crear tabla solo si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vault_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            username TEXT NOT NULL,
            encrypted_password BLOB NOT NULL,
            encrypted_notes BLOB,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            owner_id TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()



