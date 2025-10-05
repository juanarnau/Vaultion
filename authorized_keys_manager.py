# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
import json
from pathlib import Path
from datetime import datetime

AUTHORIZED_KEYS_PATH = Path.home() / ".vaultion" / "authorized_keys.json"

def load_authorized_keys():
    if not AUTHORIZED_KEYS_PATH.exists():
        return []
    with open(AUTHORIZED_KEYS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_authorized_keys(data):
    AUTHORIZED_KEYS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUTHORIZED_KEYS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_key_extended(alias, public_key, usb_id, origin="usb", comment=""):
    keys = load_authorized_keys()

    # Verificar si ya existe una clave con ese usb_id
    for entry in keys:
        if entry["usb_id"] == usb_id:
            print(f"⚠️ Ya existe una clave registrada con el ID: {usb_id}")
            return False

    new_entry = {
        "alias": alias,
        "usb_id": usb_id,
        "public_key": public_key,
        "registered_at": datetime.utcnow().isoformat() + "Z",
        "origin": origin,
        "comment": comment
    }

    keys.append(new_entry)
    save_authorized_keys(keys)
    print(f"✅ Clave '{alias}' registrada correctamente.")
    return True

def remove_key_by_index(index):
    keys = load_authorized_keys()
    if 0 <= index < len(keys):
        removed = keys.pop(index)
        save_authorized_keys(keys)
        print(f"🗑️ Clave eliminada: {removed['alias']} ({removed['usb_id']})")
        return True
    else:
        print(f"⚠️ Índice inválido: {index}")
        return False

def is_key_authorized(public_key):
    keys = load_authorized_keys()
    return any(entry["public_key"] == public_key for entry in keys)

def list_keys():
    keys = load_authorized_keys()
    for i, entry in enumerate(keys):
        print(f"{i}. 🔑 {entry['alias']} — USB: {entry['usb_id']} — Origen: {entry['origin']} — Fecha: {entry['registered_at']}")
        if entry.get("comment"):
            print(f"   📝 {entry['comment']}")

def export_key_by_index(index, filepath):
    keys = load_authorized_keys()
    if 0 <= index < len(keys):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(keys[index]["public_key"])
        print(f"📤 Clave exportada a: {filepath}")
        return True
    else:
        print(f"⚠️ Índice inválido: {index}")
        return False