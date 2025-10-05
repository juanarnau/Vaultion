# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from pathlib import Path
import hashlib
from VaultDBManager import backup_database
from AuditLogger import log_action

class SettingsWindow(QWidget):
    def __init__(self, raw_key: bytes):
        super().__init__()
        self.setWindowTitle("⚙️ Configuración de Vaultion")
        self.setFixedSize(500, 400)
        #self.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-size: 14px;")

        self.raw_key = raw_key
        self.owner_id = hashlib.sha256(raw_key).hexdigest().upper()[:16]

        layout = QVBoxLayout()

        # Identidad
        identity_label = QLabel(f"🧬 Propietario actual: {self.owner_id}")
        identity_label.setAlignment(Qt.AlignCenter)
        #identity_label.setStyleSheet("font-size: 16px; color: #00ff99;")
        layout.addWidget(identity_label)

        # Botones
        self.btn_backup = QPushButton("📦 Crear copia de seguridad")
        self.btn_export_audit = QPushButton("📄 Exportar historial de auditoría")
        self.btn_clear_cache = QPushButton("🧼 Limpiar caché local")
        self.btn_reset_ui = QPushButton("🎨 Restaurar diseño por defecto")

        self.btn_backup.clicked.connect(self.create_backup)
        self.btn_export_audit.clicked.connect(self.export_audit)
        self.btn_clear_cache.clicked.connect(self.clear_cache)
        self.btn_reset_ui.clicked.connect(self.reset_ui)

        for btn in [self.btn_backup, self.btn_export_audit, self.btn_clear_cache, self.btn_reset_ui]:
            layout.addWidget(btn)

        self.setLayout(layout)

    def create_backup(self):
        backup_database()
        log_action("Copia de seguridad", self.owner_id, "Backup manual desde configuración")
        QMessageBox.information(self, "✅ Copia creada", "Se ha creado una copia de seguridad de la base de datos.")

    def export_audit(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Exportar historial", "audit_log.json", "Archivo JSON (*.json)")
        if filename:
            try:
                from AuditLogger import LOG_PATH
                with open(LOG_PATH, "r", encoding="utf-8") as f:
                    data = f.read()
                with open(filename, "w", encoding="utf-8") as out:
                    out.write(data)
                QMessageBox.information(self, "✅ Exportación completa", f"Historial guardado en:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo exportar el historial:\n{e}")

    def clear_cache(self):
        # Placeholder: puedes limpiar archivos temporales, logs, etc.
        QMessageBox.information(self, "🧼 Caché limpiada", "Se ha limpiado la caché local.")
        log_action("Limpieza de caché", self.owner_id, "Acción manual desde configuración")

    def reset_ui(self):
        # Placeholder: puedes restaurar estilos, tamaños, etc.
        QMessageBox.information(self, "🎨 Diseño restaurado", "Se ha restaurado la interfaz a su estado original.")
        log_action("Restauración de UI", self.owner_id, "Preferencias visuales reiniciadas")