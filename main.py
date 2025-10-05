# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau

import sys
from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

# 🔧 Módulos internos
from vaultion_boot import boot_vaultion, get_database_path
from VaultDBManager import initialize_database
from UnlockScreen import UnlockScreen
from vaultion_theme import aplicar_estilo

# 🎨 Crear aplicación Qt y aplicar estilo global
app = QApplication(sys.argv)
aplicar_estilo(app)

# 🔐 Validar o generar clave desde USB
key_path = boot_vaultion()

# 📁 Inicializar base de datos
db_path = get_database_path()
initialize_database(db_path)

# 🖼️ Mostrar pantalla de carga
splash_pix = QPixmap("assets/splash.png")
splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
splash.setWindowFlag(Qt.FramelessWindowHint)
splash.showMessage("🔄 Cargando interfaz...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
splash.show()
app.processEvents()

# 🧩 Crear ventana principal
unlock = UnlockScreen()
unlock.show()

# ⏱️ Cerrar splash después de mostrar ventana principal
QTimer.singleShot(2000, lambda: splash.finish(unlock))

# 🛑 Confirmar salida si se cierra desde el botón
def confirmar_salida():
    respuesta = QMessageBox.question(
        unlock,
        "Confirmar salida",
        "¿Estás seguro de que quieres salir de Vaultion?",
        QMessageBox.Yes | QMessageBox.No
    )
    if respuesta == QMessageBox.Yes:
        app.quit()

# 🚀 Ejecutar aplicación
sys.exit(app.exec())

