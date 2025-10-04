from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from KeyManagerWindow import KeyManagerWindow

class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vaultion — Dashboard")
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: #121212; color: #ffffff; font-size: 16px;")

        layout = QVBoxLayout()

        welcome = QLabel("🔐 Vaultion desbloqueado")
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ff99;")

        btn_keys = QPushButton("🔑 Gestionar claves")
        btn_db = QPushButton("📁 Abrir base de datos")
        btn_config = QPushButton("⚙️ Configuración")

        for btn in [btn_keys, btn_db, btn_config]:
            btn.setStyleSheet("padding: 10px; font-size: 16px;")

        layout.addWidget(welcome)
        layout.addWidget(btn_keys)
        layout.addWidget(btn_db)
        layout.addWidget(btn_config)

        self.setLayout(layout)
    
    def open_key_manager(self):
        self.key_manager = KeyManagerWindow()
        self.key_manager.show()
