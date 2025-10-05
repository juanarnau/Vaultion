# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QFileDialog, QInputDialog, QMessageBox, QStyle
)
from PySide6.QtCore import Qt
from pathlib import Path
import json
import hashlib
import platform
import psutil
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

AUTHORIZED_KEYS_PATH = Path("authorized_keys.json")

class KeyManagerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vaultion — Gestión de Claves")
        self.setFixedSize(700, 500)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-size: 14px;")

        layout = QVBoxLayout()

        title = QLabel("🔑 Claves autorizadas")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff99;")
        layout.addWidget(title)

        button_bar = QHBoxLayout()
        btn_generate_rsa = QPushButton("🛠️ Generar nueva clave RSA")
        btn_import_key = QPushButton("📥 Importar clave existente")
        btn_generate_usb = QPushButton("💾 Generar USB Vaultion")

        btn_generate_rsa.clicked.connect(self.generate_rsa_key)
        btn_import_key.clicked.connect(self.import_existing_key)
        btn_generate_usb.clicked.connect(self.generate_usb_key)

        button_bar.addWidget(btn_generate_rsa)
        button_bar.addWidget(btn_import_key)
        button_bar.addWidget(btn_generate_usb)
        layout.addLayout(button_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Alias", "ID", "Acciones"])
        self.table.setStyleSheet("background-color: #2e2e2e;")
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_keys()

    def load_keys(self):
        self.table.setRowCount(0)
        if not AUTHORIZED_KEYS_PATH.exists():
            return

        with open(AUTHORIZED_KEYS_PATH, "r", encoding="utf-8") as f:
            keys = json.load(f)

        for i, entry in enumerate(keys):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(entry["alias"]))
            self.table.setItem(i, 1, QTableWidgetItem(entry["usb_id"]))

            # Botón exportar .pem
            btn_export = QPushButton()
            btn_export.setIcon(btn_export.style().standardIcon(QStyle.SP_DialogOpenButton))

            btn_export.setToolTip("Exportar .pem")
            btn_export.setStyleSheet("border: none; padding: 4px;")
            btn_export.clicked.connect(lambda _, e=entry: self.export_key(e))

            # Botón guardar como vaultion.key
            btn_export_local = QPushButton()
            btn_export_local.setIcon(btn_export_local.style().standardIcon(QStyle.SP_DialogSaveButton))
            btn_export_local.setToolTip("Guardar como vaultion.key")
            btn_export_local.setStyleSheet("border: none; padding: 4px;")
            btn_export_local.clicked.connect(lambda _, e=entry: self.export_to_local_keyfile(e))

            # Botón revocar
            btn_revoke = QPushButton()
            btn_revoke.setIcon(btn_revoke.style().standardIcon(QStyle.SP_TrashIcon))
            btn_revoke.setToolTip("Revocar clave")
            btn_revoke.setStyleSheet("border: none; padding: 4px;")
            btn_revoke.clicked.connect(lambda _, idx=i: self.revoke_key(idx))

            # Agrupar botones en layout
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.addWidget(btn_export)
            action_layout.addWidget(btn_export_local)
            action_layout.addWidget(btn_revoke)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)
            action_layout.setAlignment(Qt.AlignCenter)

            self.table.setCellWidget(i, 2, action_widget)

    def export_key(self, entry):
        filename, _ = QFileDialog.getSaveFileName(self, "Exportar clave pública", f"{entry['alias']}.pem", "PEM Files (*.pem)")
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(entry["public_key"])

    def export_to_local_keyfile(self, entry):
        with open("vaultion.key", "w", encoding="utf-8") as f:
            f.write(entry["public_key"])
        QMessageBox.information(self, "✅ Clave exportada", "Se ha guardado la clave como vaultion.key")

    def revoke_key(self, index):
        with open(AUTHORIZED_KEYS_PATH, "r", encoding="utf-8") as f:
            keys = json.load(f)
        removed = keys.pop(index)
        with open(AUTHORIZED_KEYS_PATH, "w", encoding="utf-8") as f:
            json.dump(keys, f, indent=2)
        self.load_keys()

    def generate_rsa_key(self):
        alias, ok = QInputDialog.getText(self, "Alias de clave", "Introduce un alias para la nueva clave:")
        if not ok or not alias:
            return

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        usb_id = hashlib.sha256(alias.encode()).hexdigest()[:16]
        entry = {
            "alias": alias,
            "usb_id": usb_id,
            "public_key": pem
        }

        self.save_key_entry(entry)
        QMessageBox.information(self, "✅ Clave generada", f"Clave RSA creada con alias: {alias}")
        self.load_keys()

    def import_existing_key(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecciona archivo PEM", "", "PEM Files (*.pem)")
        if not file_path:
            return

        alias, ok = QInputDialog.getText(self, "Alias de clave", "Introduce un alias para esta clave:")
        if not ok or not alias:
            return

        with open(file_path, "r", encoding="utf-8") as f:
            pem = f.read()

        usb_id = hashlib.sha256(alias.encode()).hexdigest()[:16]
        entry = {
            "alias": alias,
            "usb_id": usb_id,
            "public_key": pem
        }

        self.save_key_entry(entry)
        QMessageBox.information(self, "✅ Clave importada", f"Clave importada con alias: {alias}")
        self.load_keys()

    def save_key_entry(self, entry: dict):
        if AUTHORIZED_KEYS_PATH.exists():
            with open(AUTHORIZED_KEYS_PATH, "r", encoding="utf-8") as f:
                keys = json.load(f)
        else:
            keys = []

        keys.append(entry)
        with open(AUTHORIZED_KEYS_PATH, "w", encoding="utf-8") as f:
            json.dump(keys, f, indent=2)

    def export_structured_key(self, entry, target_path):
        structured = {
            "message": entry["usb_id"],
            "signature": "dummy_signature",  # puedes firmarlo más adelante
            "public_key": entry["public_key"]
        }

        # Validación: solo permitir escritura si el archivo es vaultion.key
        if target_path.name != "vaultion.key":
            QMessageBox.critical(self, "Error de seguridad", "Solo se permite escribir vaultion.key en el USB.")
            return

        try:
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(structured, f, indent=2)
            print(f"✅ Clave escrita en USB: {target_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo escribir la clave:\n{e}")
            import traceback
            traceback.print_exc()

    def generate_usb_key(self):
        drives = self.get_removable_drives()
        if not drives:
            QMessageBox.warning(self, "Sin USB", "No se detectó ninguna unidad USB conectada.")
            return

        drive_labels = [str(drive) for drive in drives]
        selected, ok = QInputDialog.getItem(self, "Seleccionar USB", "Unidades disponibles:", drive_labels, 0, False)
        if not ok or not selected:
            return

        usb_path = Path(selected)

        # Validar que el USB no contiene archivos sensibles
        allowed_files = {"vaultion.key"}
        actual_files = {f.name for f in usb_path.iterdir() if f.is_file()}
        if not actual_files.issubset(allowed_files):
            QMessageBox.warning(self, "Advertencia", "El USB contiene archivos no autorizados.\nSe recomienda usar un USB limpio.")
            print(f"⚠️ Archivos encontrados en USB: {actual_files - allowed_files}")

        if not AUTHORIZED_KEYS_PATH.exists():
            QMessageBox.warning(self, "Sin claves", "No hay claves autorizadas para exportar.")
            return

        with open(AUTHORIZED_KEYS_PATH, "r", encoding="utf-8") as f:
            keys = json.load(f)

        if not keys:
            QMessageBox.warning(self, "Sin claves", "No hay claves disponibles.")
            return

        selected_entry = keys[0]
        target_path = usb_path / "vaultion.key"

        self.export_structured_key(selected_entry, target_path)

    def get_removable_drives(self):
        system = platform.system()
        drives = []

        if system == "Windows":
            import ctypes
            import string
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for i in range(26):
                if bitmask & (1 << i):
                    drive_letter = f"{string.ascii_uppercase[i]}:\\"
                    drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_letter)
                    if drive_type == 2:
                        drives.append(Path(drive_letter))

        elif system in ("Linux", "Darwin"):
            for part in psutil.disk_partitions(all=False):
                if "media" in part.mountpoint or "Volumes" in part.mountpoint:
                    drives.append(Path(part.mountpoint))

        return drives
    
    def import_key_entry(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar clave",
            "",
            "Claves Vaultion (*.key);;Claves públicas (*.pem)"
        )

        if not file_path:
            return

        try:
            if file_path.endswith(".key"):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    public_key = data.get("public_key")
                    usb_id = data.get("message")
                    alias = "Importado desde USB"
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    public_key = f.read()
                    usb_id = self.generate_usb_id(public_key)
                    alias = "Importado desde PEM"

            if not public_key or not usb_id:
                QMessageBox.warning(self, "Error", "La clave está incompleta o mal formada.")
                return

            entry = {
                "alias": alias,
                "usb_id": usb_id,
                "public_key": public_key
            }

            self.save_key_entry(entry)
            QMessageBox.information(self, "✅ Clave importada", f"Alias: {alias}\nID: {usb_id}")
            print(f"🔑 Clave importada: {entry}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo importar la clave:\n{e}")
            import traceback
            traceback.print_exc()