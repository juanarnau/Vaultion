# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QAbstractItemView, QDialog, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from VaultDBManager import get_entries, delete_entry, update_entry, decrypt_field
import hashlib
from AddEntryDialog import AddEntryDialog

class VaultDatabaseWindow(QWidget):
    def __init__(self, key: bytes, raw_key: bytes):
        super().__init__()
        self.setWindowTitle("Vaultion — Base de Datos")
        self.setFixedSize(700, 500)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-size: 14px;")
        self.key = key
        self.raw_key = raw_key
        self.owner_id = hashlib.sha256(raw_key).hexdigest().upper()[:16]

        layout = QVBoxLayout()

        title = QLabel(f"🔐 Entradas cifradas — Propietario: {self.owner_id}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff99;")
        layout.addWidget(title)

        button_bar = QHBoxLayout()
        self.btn_add = QPushButton("➕ Añadir entrada")
        self.btn_refresh = QPushButton("🔄 Refrescar")
        self.btn_save_changes = QPushButton("💾 Guardar cambios")
        #self.btn_delete_selected = QPushButton("🗑️ Eliminar seleccionada")

        self.btn_add.clicked.connect(self.add_entry)
        self.btn_refresh.clicked.connect(self.load_entries)
        self.btn_save_changes.clicked.connect(self.save_changes)
        #self.btn_delete_selected.clicked.connect(self.delete_selected)

        button_bar.addWidget(self.btn_add)
        button_bar.addWidget(self.btn_refresh)
        button_bar.addWidget(self.btn_save_changes)
        #button_bar.addWidget(self.btn_delete_selected)
        layout.addLayout(button_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Servicio", "Usuario", "Contraseña", "Notas", "Creado", "Acciones"])
        self.table.setStyleSheet("background-color: #2e2e2e;")
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_entries()

    def load_entries(self):
        self.table.setRowCount(0)
        try:
            entries = get_entries(self.key, owner_id=self.owner_id)
            print("📥 Obteniendo entradas...")
            print(f"🔍 Entradas encontradas: {len(entries)}")

            for i, entry in enumerate(entries):
                self.table.insertRow(i)
                print(f"🔍 Procesando entrada ID {entry.get('id')} — Servicio: {entry.get('service')}")
                try:
                    if not isinstance(entry["encrypted_password"], bytes):
                        raise TypeError("Campo 'encrypted_password' no es bytes")
                    if not isinstance(entry["encrypted_notes"], bytes):
                        raise TypeError("Campo 'encrypted_notes' no es bytes")

                    decrypted_password = decrypt_field(entry["encrypted_password"], self.key)
                    decrypted_notes = decrypt_field(entry["encrypted_notes"], self.key)
                except Exception as e:
                    decrypted_password = "❌ Error"
                    decrypted_notes = "❌ Error"
                    print(f"⚠️ Error al descifrar entrada {entry.get('id')}: {e}")
                    QMessageBox.warning(self, "Error de descifrado",
                        f"No se pudo descifrar la entrada ID {entry.get('id')} ({entry.get('service')}):\n{e}")

                service_item = QTableWidgetItem(entry["service"])
                username_item = QTableWidgetItem(entry["username"])
                password_item = QTableWidgetItem(decrypted_password)
                notes_item = QTableWidgetItem(decrypted_notes)
                created_item = QTableWidgetItem(entry["created_at"])

                service_item.setData(Qt.UserRole, entry["id"])

                self.table.setItem(i, 0, service_item)
                self.table.setItem(i, 1, username_item)
                self.table.setItem(i, 2, password_item)
                self.table.setItem(i, 3, notes_item)
                self.table.setItem(i, 4, created_item)

                btn_delete = QPushButton("🗑️")
                btn_delete.clicked.connect(lambda _, eid=entry["id"]: self.delete_entry(eid))

                action_layout = QHBoxLayout()
                action_layout.setContentsMargins(0, 0, 0, 0)
                action_layout.addWidget(btn_delete)

                action_widget = QWidget()
                action_widget.setLayout(action_layout)
                self.table.setCellWidget(i, 5, action_widget)

        except Exception as e:
            import traceback
            print("❌ Error global al abrir la base de datos:")
            traceback.print_exc()  # ✅ Esto imprime el stack completo
            QMessageBox.critical(self, "Error", f"No se pudo abrir la base de datos:\n{e}")


    def delete_entry(self, entry_id):
        confirm = QMessageBox.question(self, "Confirmar eliminación", "¿Eliminar esta entrada?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            delete_entry(entry_id)
            self.load_entries()

    def delete_selected(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Sin selección", "Selecciona una fila para eliminar.")
            return
        item = self.table.item(selected, 0)
        if item:
            entry_id = item.data(Qt.UserRole)
            self.delete_entry(entry_id)

    def add_entry(self):
        dialog = AddEntryDialog(self.key, self.owner_id)
        if dialog.exec() == QDialog.Accepted:

            self.load_entries()

    def handle_cell_edit(self, row, column):
        print(f"✏️ Editando celda en fila {row}, columna {column}")
        try:
            def safe_text(r, c):
                item = self.table.item(r, c)
                return item.text() if item else ""

            service = safe_text(row, 0)
            username = safe_text(row, 1)
            password = safe_text(row, 2)
            notes = safe_text(row, 3)

            id_item = self.table.item(row, 0)
            entry_id = id_item.data(Qt.UserRole) if id_item else None

            if entry_id is None:
                raise ValueError("ID de entrada no disponible")

            update_entry(entry_id, service, username, password, notes, self.key)
            print(f"✅ Entrada {entry_id} actualizada.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el cambio:\n{e}")

    def save_changes(self):
        print("💾 Guardando cambios...")
        try:
            for row in range(self.table.rowCount()):
                def safe_text(col):
                    item = self.table.item(row, col)
                    return item.text() if item else ""

                service = safe_text(0)
                username = safe_text(1)
                password = safe_text(2)
                notes = safe_text(3)

                id_item = self.table.item(row, 0)
                entry_id = id_item.data(Qt.UserRole) if id_item else None
                if entry_id is None:
                    continue

                update_entry(entry_id, service, username, password, notes, self.key)

            QMessageBox.information(self, "✅ Cambios guardados", "Todas las ediciones han sido guardadas correctamente.")
            self.load_entries()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar los cambios:\n{e}")

    def verify_entry_structure(self, entries: list):
        errores = []

        for i, entry in enumerate(entries):
            eid = entry.get("id")
            service = entry.get("service", "¿Sin servicio?")
            if eid is None or not isinstance(eid, int):
                errores.append({"id": eid, "service": service, "error": "ID inválido o ausente"})

            if "encrypted_password" not in entry:
                errores.append({"id": eid, "service": service, "error": "Falta 'encrypted_password'"})
            elif not isinstance(entry["encrypted_password"], bytes):
                errores.append({"id": eid, "service": service, "error": "'encrypted_password' no es bytes"})

            if "encrypted_notes" not in entry:
                errores.append({"id": eid, "service": service, "error": "Falta 'encrypted_notes'"})
            elif not isinstance(entry["encrypted_notes"], bytes):
                errores.append({"id": eid, "service": service, "error": "'encrypted_notes' no es bytes"})

            if "created_at" not in entry:
                errores.append({"id": eid, "service": service, "error": "Falta 'created_at'"})

            try:
                _ = decrypt_field(entry["encrypted_password"], self.key)
                _ = decrypt_field(entry["encrypted_notes"], self.key)
            except Exception as e:
                errores.append({"id": eid, "service": service, "error": f"Error al descifrar: {e}"})

        if errores:
            dialog = ErrorReportDialog(errores)
            dialog.exec()
        else:
            QMessageBox.information(self, "✅ Verificación", "Todas las entradas tienen estructura válida.")

class ErrorReportDialog(QDialog):
    def __init__(self, errores: list):
        super().__init__()
        self.setWindowTitle("🔍 Informe de errores en entradas")
        self.setFixedSize(700, 400)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-size: 13px;")

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Servicio", "Error"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: #2e2e2e;")

        self.table.setRowCount(len(errores))
        for i, err in enumerate(errores):
            eid_item = QTableWidgetItem(str(err.get("id", "❓")))
            service_item = QTableWidgetItem(err.get("service", "❓"))
            error_item = QTableWidgetItem(err["error"])

            eid_item.setForeground(Qt.red)
            error_item.setForeground(Qt.yellow)

            self.table.setItem(i, 0, eid_item)
            self.table.setItem(i, 1, service_item)
            self.table.setItem(i, 2, error_item)

        layout.addWidget(self.table)
        self.setLayout(layout)