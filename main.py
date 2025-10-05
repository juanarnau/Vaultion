# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau
 
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
import sys

from vaultion_boot import boot_vaultion, get_database_path
from VaultDBManager import initialize_database
from UnlockScreen import UnlockScreen

# 🧠 Crear aplicación Qt
app = QApplication([])

# 🔐 Validar o generar clave desde USB
key_path = boot_vaultion()

# 📁 Obtener ruta de base de datos y crear tabla si no existe
db_path = get_database_path()
initialize_database(db_path)

# 🖼️ Mostrar splash screen
splash_pix = QPixmap("assets/splash.png")
splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
splash.setWindowFlag(Qt.FramelessWindowHint)
splash.showMessage("🔄 Cargando interfaz...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
splash.show()
app.processEvents()

# 🧩 Crear ventana principal
unlock = UnlockScreen()
unlock.show()

# ⏱️ Cerrar splash después de mostrar ventana
QTimer.singleShot(2000, lambda: splash.finish(unlock))

# 🚀 Ejecutar aplicación
sys.exit(app.exec())