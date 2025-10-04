from VaultDBManager import add_entry
import secrets
import string
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox, QApplication

class AddEntryDialog(QDialog):
    def __init__(self, key: bytes, owner_id: str):
        super().__init__(None)
        self.setWindowTitle("➕ Nueva entrada")
        self.setFixedSize(400, 350)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-size: 14px;")
        self.key = key
        self.owner_id = owner_id

        layout = QVBoxLayout()

        self.service_input = QLineEdit()
        self.service_input.setPlaceholderText("Servicio (ej. GitHub)")
        layout.addWidget(QLabel("🔧 Servicio:"))
        layout.addWidget(self.service_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario")
        layout.addWidget(QLabel("👤 Usuario:"))
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.btn_generate = QPushButton("🎲 Generar contraseña segura")
        self.btn_copy = QPushButton("📋 Copiar al portapapeles")
        btn_pw_layout = QHBoxLayout()
        btn_pw_layout.addWidget(self.btn_generate)
        btn_pw_layout.addWidget(self.btn_copy)
        layout.addLayout(btn_pw_layout)

        self.btn_generate.clicked.connect(self.fill_generated_password)
        self.btn_copy.clicked.connect(self.copy_password_to_clipboard)
        layout.addWidget(QLabel("🔐 Contraseña:"))
        layout.addWidget(self.password_input)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notas opcionales")
        layout.addWidget(QLabel("📝 Notas:"))
        layout.addWidget(self.notes_input)

        self.btn_save = QPushButton("💾 Guardar entrada")
        self.btn_save.clicked.connect(self.save_entry)
        layout.addWidget(self.btn_save)

        self.setLayout(layout)

    def save_entry(self):
        service = self.service_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        notes = self.notes_input.toPlainText().strip()

        if not service or not username or not password:
            QMessageBox.warning(self, "Campos incompletos", "Servicio, usuario y contraseña son obligatorios.")
            return
        if len(password) < 12 or not any(c in string.punctuation for c in password):
            QMessageBox.warning(self, "Contraseña débil", "Usa al menos 12 caracteres y símbolos especiales.")
            return
        add_entry(self.key, service, username, password, notes, owner_id=self.owner_id)
        QMessageBox.information(self, "✅ Entrada añadida", f"Se ha guardado la entrada para {service}.")
        self.accept()
    def generate_password(self, length=16):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    def fill_generated_password(self):
        pw = self.generate_password()
        self.password_input.setText(pw)

    def copy_password_to_clipboard(self):
        pw = self.password_input.text()
        if pw:
            clipboard = QApplication.clipboard()
            clipboard.setText(pw)
            QMessageBox.information(self, "📋 Copiado", "Contraseña copiada al portapapeles.")
        else:
            QMessageBox.warning(self, "⚠️ Vacío", "No hay contraseña para copiar.")