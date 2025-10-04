import json
from datetime import datetime
from pathlib import Path

LOG_PATH = Path.home() / ".vaultion" / "audit_log.json"

def log_action(action: str, owner_id: str, details: str = ""):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "owner_id": owner_id,
        "details": details
    }
    logs = []
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            logs = json.load(f)
    logs.append(entry)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)