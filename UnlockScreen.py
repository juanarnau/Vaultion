# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
import sys
from VaultDBManager import derive_key, initialize_database
from vaultion_boot import boot_vaultion
from KeyManagerWindow import KeyManagerWindow
from VaultDatabaseWindow import VaultDatabaseWindow  # Asegúrate de tener este módulo
from SettingsWindow import SettingsWindow            # Asegúrate de tener este módulo
from pathlib import Path
from DiagnosticsWindow import DiagnosticsWindow
from PySide6.QtGui import QIcon
from pathlib import Path
from vaultion_boot import detect_usb_key, generate_new_key
from vaultion_boot import get_database_path
from VaultDBManager import initialize_database

KEY_PATH = Path("D:/vaultion.key")  # Ajusta según tu ruta real
KEY_FILE_PATH = Path("vaultion.key")

class UnlockScreen(QWidget):
    def __init__(self, recurso_empaquetado):
        super().__init__()
        self.setWindowTitle("Vaultion — Desbloqueo USB")

        # 🖼️ Cargar icono desde recurso empaquetado
        icon_path = recurso_empaquetado("assets/icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.setFixedSize(500, 300)
        layout = QVBoxLayout()

        # 🔐 Mensaje de estado
        self.status_label = QLabel("🔒 Inserta tu USB para desbloquear Vaultion")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

        # 🚀 Mensaje de bienvenida
        self.welcome_label = QLabel("🚀 Bienvenido a Vaultion")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setObjectName("welcomeLabel")
        layout.addWidget(self.welcome_label)

        # 🧩 Botones del dashboard
        self.btn_keys = QPushButton("🔑 Gestionar claves")
        self.btn_db = QPushButton("📁 Abrir base de datos")
        self.btn_diag = QPushButton("🧪 Diagnóstico")
        self.btn_config = QPushButton("⚙️ Configuración")

        for btn in [self.btn_keys, self.btn_db, self.btn_config, self.btn_diag]:
            btn.setVisible(False)
            layout.addWidget(btn)

        layout.addStretch()

        # ❌ Botón de salida
        self.btn_exit = QPushButton("❌ Salir de Vaultion")
        self.btn_exit.setObjectName("exitButton")
        self.btn_exit.clicked.connect(self.close)
        layout.addWidget(self.btn_exit)

        self.setLayout(layout)

        # 🔗 Conectar botones
        self.btn_keys.clicked.connect(self.open_key_manager)
        self.btn_db.clicked.connect(self.open_database)
        self.btn_diag.clicked.connect(self.open_diagnostics)
        self.btn_config.clicked.connect(self.open_settings)

        # ⏱️ Ejecutar verificación USB después de mostrar la ventana
        QTimer.singleShot(100, self.check_usb)

    def closeEvent(self, event):
        respuesta = QMessageBox.question(
            self,
            "Confirmar salida",
            "¿Estás seguro de que quieres salir de Vaultion?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def closeEvent(self, event):
        respuesta = QMessageBox.question(
            self,
            "Confirmar salida",
            "¿Estás seguro de que quieres salir de Vaultion?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def close_app(self):
        QApplication.quit()

    def check_usb(self):
        key_file = boot_vaultion()
        db_path = get_database_path()

        if key_file and key_file != "invalid":
            try:
                with open(key_file, "rb") as f:
                    raw_key = f.read()
                self.raw_key = raw_key
                self.key = derive_key(raw_key)
                initialize_database(db_path)
                self.status_label.setText("✅ USB autorizado. Accediendo...")
                self.status_label.setStyleSheet("color: #00ff99; font-size: 16px;")
                self.show_dashboard_buttons()
            except Exception as e:
                self.status_label.setText("❌ Error al procesar la clave.")
                QMessageBox.critical(self, "Error", f"No se pudo procesar la clave:\n{e}")

        elif key_file == "invalid":
            self.status_label.setText("❌ Clave inválida. Acceso denegado.")
            QMessageBox.critical(self, "Error", "La clave encontrada es inválida.\nNo se puede continuar.")
            self.close()
            QApplication.instance().quit()

        else:
            reply = QMessageBox.question(
                self,
                "Clave no encontrada",
                "No se encontró una clave Vaultion.\n¿Deseas generar una nueva en el USB conectado?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                usb_path = detect_usb_path()
                if usb_path:
                    key_path = usb_path / "vaultion.key"
                    try:
                        create_new_key(key_path)
                        QMessageBox.information(self, "Clave creada", f"Se ha generado una nueva clave en:\n{key_path}")
                        QTimer.singleShot(100, self.check_usb)
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"No se pudo crear la clave:\n{e}")
                else:
                    QMessageBox.critical(self, "Error", "No se detectó ningún USB válido.")
            else:
                QMessageBox.critical(self, "Error", "No se puede continuar sin una clave Vaultion.")
                self.close()
                QApplication.instance().quit()

    def show_dashboard_buttons(self):
        self.btn_keys.setVisible(True)
        self.btn_db.setVisible(True)
        self.btn_config.setVisible(True)
        self.btn_diag.setVisible(True)

    def open_key_manager(self):
        self.key_window = KeyManagerWindow()
        self.key_window.show()

    def open_database(self):
        try:
            self.db_window = VaultDatabaseWindow(self.key, self.raw_key)
            self.db_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la base de datos:\n{e}")

    def open_settings(self):
        try:
            self.settings_window = SettingsWindow(self.raw_key)
            self.settings_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la configuración:\n{e}")

    def open_master_key_manager(self):
        self.master_key_window = MasterKeyWindow()
        self.master_key_window.show()

    def open_diagnostics(self):
        try:
            self.diag_window = DiagnosticsWindow(self.key, self.raw_key)
            self.diag_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el diagnóstico:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    unlock = UnlockScreen()
    unlock.show()
    sys.exit(app.exec())