# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt
from VaultDBManager import get_entries
import hashlib

class DiagnosticsWindow(QWidget):
    def __init__(self, key: bytes, raw_key: bytes):
        super().__init__()
        self.setWindowTitle("🧪 Diagnóstico de Vaultion")
        self.setFixedSize(600, 300)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-size: 14px;")

        self.key = key
        self.raw_key = raw_key
        self.owner_id = hashlib.sha256(raw_key).hexdigest().upper()[:16]
        self.fingerprint = hashlib.sha256(raw_key).hexdigest().upper()

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"🔐 Fingerprint SHA-256:\n{self.fingerprint}"))
        layout.addWidget(QLabel(f"🧬 Propietario:\n{self.owner_id}"))

        self.entry_count_label = QLabel("📊 Entradas cifradas: ...")
        layout.addWidget(self.entry_count_label)

        self.btn_scan = QPushButton("🔍 Escanear integridad")
        self.btn_scan.clicked.connect(self.scan_database)
        layout.addWidget(self.btn_scan)

        self.setLayout(layout)
        self.update_entry_count()

    def update_entry_count(self):
        try:
            entries = get_entries(self.key, owner_id=self.owner_id)
            self.entry_count_label.setText(f"📊 Entradas cifradas: {len(entries)}")
        except Exception as e:
            self.entry_count_label.setText("📊 Error al contar entradas")
            QMessageBox.critical(self, "Error", f"No se pudo acceder a la base:\n{e}")

    def scan_database(self):
        try:
            entries = get_entries(self.key, owner_id=self.owner_id)
            duplicates = set()
            seen = set()
            for entry in entries:
                key = (entry["service"].lower(), entry["username"].lower())
                if key in seen:
                    duplicates.add(key)
                seen.add(key)

            if duplicates:
                msg = "\n".join([f"{s} / {u}" for s, u in duplicates])
                QMessageBox.warning(self, "⚠️ Duplicados detectados", f"Se han detectado entradas duplicadas:\n{msg}")
            else:
                QMessageBox.information(self, "✅ Todo correcto", "No se han detectado duplicados ni errores.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo escanear la base:\n{e}")