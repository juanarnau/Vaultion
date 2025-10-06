# Copyright © 2025 Juan Arnau
# Licencia de uso restringido – ver LICENSE.txt
# Juan Arnau

import sys
import os
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

# 🔧 Módulos internos
from vaultion_boot import boot_vaultion, get_database_path
from VaultDBManager import initialize_database
from UnlockScreen import UnlockScreen
from vaultion_theme import aplicar_estilo

# 📦 Acceso a recursos empaquetados (PyInstaller)
def recurso_empaquetado(ruta_relativa):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)

# 🎨 Crear aplicación Qt y aplicar estilo global
app = QApplication(sys.argv)
aplicar_estilo(app)

# 🔐 Validar o generar clave desde USB
key_path = boot_vaultion()

# 📁 Inicializar base de datos
db_path = get_database_path()
initialize_database(db_path)

# 🖼️ Mostrar pantalla de carga
splash_path = recurso_empaquetado("assets/splash.png")
splash_pix = QPixmap(splash_path)
splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
splash.setWindowFlag(Qt.FramelessWindowHint)
splash.showMessage("🔄 Cargando interfaz...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
splash.show()
app.processEvents()

# 🧩 Crear ventana principal
unlock = UnlockScreen(recurso_empaquetado)  # Pasamos la función para usarla en iconos
unlock.show()

# ⏱️ Cerrar splash después de mostrar ventana principal
QTimer.singleShot(2000, lambda: splash.finish(unlock))

# 🚀 Ejecutar aplicación
sys.exit(app.exec())
