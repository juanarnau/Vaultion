# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QMessageBox
from authorized_keys_manager import list_keys, remove_key

class KeyManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de claves USB autorizadas")
        self.setMinimumSize(400, 300)

        self.layout = QVBoxLayout()
        self.key_list = QListWidget()
        self.refresh_keys()

        self.remove_button = QPushButton("Revocar clave seleccionada")
        self.remove_button.clicked.connect(self.revoke_selected_key)

        self.layout.addWidget(self.key_list)
        self.layout.addWidget(self.remove_button)
        self.setLayout(self.layout)

    def refresh_keys(self):
        self.key_list.clear()
        keys = list_keys()
        for alias, info in keys.items():
            self.key_list.addItem(f"{alias} — USB: {info['usb_id']} — Añadida: {info['added']}")

    def revoke_selected_key(self):
        selected = self.key_list.currentItem()
        if selected:
            alias = selected.text().split(" — ")[0]
            confirm = QMessageBox.question(self, "Confirmar", f"¿Eliminar clave '{alias}'?")
            if confirm == QMessageBox.Yes:
                remove_key(alias)
                self.refresh_keys()