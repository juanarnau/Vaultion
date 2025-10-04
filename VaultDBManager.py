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

    print("🔍 Nonce:", nonce)
    print("🔍 Longitud del nonce:", len(nonce))
    print("🔍 Tipo del nonce:", type(nonce))
    print("🔍 ¿Está vacío?:", nonce == b"")
    print("🧪 Usando decrypt_data con validación")
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
        print(f"✅ Entrada añadida: {service} ({username})")
        print("🔍 Tipo de encrypted_pw:", type(encrypted_pw), "Longitud:", len(encrypted_pw))
        print("🔍 Tipo de encrypted_notes:", type(encrypted_notes), "Longitud:", len(encrypted_notes))
        print("🔍 Preview nonce:", encrypted_pw[:16])

    except Exception as e:
        print(f"❌ Error al añadir entrada: {e}")
    finally:
        conn.close()

def sanitize_blob(blob):
    return bytes(blob) if not isinstance(blob, bytes) else blob

def safe_decrypt(blob, key: bytes) -> str:
    if not blob:
        print("🛑 Blob vacío o None, no se descifra")
        return ""
    if not isinstance(blob, (bytes, bytearray)):
        print(f"🛑 Tipo inválido: {type(blob)}")
        return ""
    if len(blob) < 32:
        print(f"🛑 Blob demasiado corto: {len(blob)} bytes")
        return ""
    try:
        return decrypt_data(key, blob)
    except Exception as e:
        print(f"⚠️ Error en safe_decrypt: {e}")
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
            print("❌ encrypted_password no es bytes, reconvirtiendo...")
            pw_blob = sanitize_blob(row[3])

        if notes_blob and not isinstance(notes_blob, bytes):
            print("❌ encrypted_notes no es bytes, reconvirtiendo...")
            notes_blob = row[4]  # sin sanitizar, lo maneja safe_decrypt
            print("🔍 Tipo real tras conversión:", type(pw_blob))
        # 🔓 Descifrado seguro
        try:
            print("🔍 Tipo final antes de decrypt_data:", type(pw_blob))
            print("🔍 Longitud final:", len(pw_blob))

            decrypted_pw = decrypt_data(key, pw_blob)
            decrypted_notes = safe_decrypt(notes_blob, key)

        except Exception as e:
            decrypted_pw = "❌ Error"
            decrypted_notes = "❌ Error"
            print(f"⚠️ Error al descifrar entrada ID {entry_id}: {e}")

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
            print(f"🔧 Reparando entrada ID {entry_id} — notas cifradas inválidas")
            fixed_blob = encrypt_data(key, "-")
            cursor.execute("UPDATE entries SET encrypted_notes = ? WHERE id = ?", (fixed_blob, entry_id))
            repaired += 1

    conn.commit()
    conn.close()
    print(f"✅ Reparación completada: {repaired} entradas corregidas")

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
    print(f"🔄 Filas modificadas: {conn.total_changes}")
    conn.close()

def sanitize_blob(blob):
    if isinstance(blob, memoryview):
        print("⚠️ Convertido desde memoryview")
        return blob.tobytes()
    if isinstance(blob, str):
        print("⚠️ Convertido desde str")
        return bytes(blob, 'latin1')
    if not isinstance(blob, bytes):
        print(f"⚠️ Convertido desde {type(blob)}")
        return bytes(blob)
    return blob

# 🗑️ Eliminar entrada
def delete_entry(entry_id: int):
    conn = sqlite3.connect(get_database_path())
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vault_entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    print(f"🗑️ Entrada eliminada: ID {entry_id}")

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
    print("🔄 Todas las entradas han sido re-cifradas con la nueva clave.")

# 🧯 Copia de seguridad
def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = VAULTION_HOME / f"vaultion_backup_{timestamp}.db"
    shutil.copy(DB_PATH, backup_path)
    print(f"🧯 Copia de seguridad creada en: {backup_path}")

def inspect_encrypted_entry(entry_id: int, encrypted_pw: bytes, encrypted_notes: bytes = b""):
    print(f"\n🔍 Inspección de entrada ID {entry_id}")

    def inspect_blob(label: str, blob: bytes):
        print(f"\n📦 Campo: {label}")
        print(f"🔹 Tipo: {type(blob)}")
        print(f"🔹 Longitud total: {len(blob)}")

        if not isinstance(blob, bytes):
            print("❌ No es tipo bytes")
            return

        if len(blob) < 32:
            print("❌ Bloque cifrado demasiado corto")
            return

        nonce = blob[:16]
        tag = blob[16:32]
        ciphertext = blob[32:]

        print(f"🔸 Nonce: {nonce}")
        print(f"🔸 Tag: {tag}")
        print(f"🔸 Ciphertext (preview): {ciphertext[:16]}...")
        print(f"🔸 Longitudes → nonce: {len(nonce)}, tag: {len(tag)}, ciphertext: {len(ciphertext)}")

    inspect_blob("Contraseña cifrada", encrypted_pw)
    if encrypted_notes:
        inspect_blob("Notas cifradas", encrypted_notes)
    else:
        print("\n📦 Campo: Notas cifradas — vacío")

    print("✅ Inspección completada\n")

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



