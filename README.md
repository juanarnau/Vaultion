# 🔐 Vaultion

**Vaultion** es un gestor de contraseñas cifradas con autenticación USB, interfaz Qt y herramientas de auditoría interna. Diseñado para entornos donde la seguridad, la transparencia y el control del usuario son prioritarios.

---

## 🚀 Características principales

- **Cifrado fuerte con clave USB**  
- **Interfaz gráfica Qt**  
- **Auditoría interna de código y recursos**  
- **Gestión avanzada de claves RSA**  
- **Reparación automática de entradas corruptas**  
- **Licencia de uso restringido**

---

## 🧠 Arquitectura del proyecto
```
VAULTION/
├── main.py                  # Punto de entrada
├── vaultion_boot.py         # Carga y verificación de clave USB
├── VaultDBManager.py        # Acceso y reparación de base de datos
├── UnlockScreen.py          # Pantalla de desbloqueo
├── AddEntryDialog.py        # Diálogo para añadir entradas
├── KeyManagerWindow.py      # Gestión visual de claves
├── SettingsWindow.py        # Preferencias y mantenimiento
├── assets/                  # Iconos y recursos gráficos
└── LICENSE.txt              # Licencia personalizada
```
---

## 🔧 Requisitos

- Python 3.11+
- PySide6
- cryptography
- sqlite3 (incluido en Python estándar)

Instalación de dependencias:

```bash
pip install -r requirements.txt
```

---

## 🖥️ Ejecución
Desde la raíz del proyecto:
```
python main.py
```
---

## 📋 Licencia
Este software está protegido por una Licencia de Uso Restringido.
No se permite el uso comercial, institucional ni lucrativo sin autorización expresa del autor.
Ver LICENSE.txt para más detalles.

---

## 📬 Contacto
Juan Arnau
📧 juan.arnau@outlook.es

---

## 🧪 Auditoría interna
Vaultion incluye un módulo de diagnóstico (vaultion_auditor.py) que detecta:
- Funciones no llamadas
- Archivos no referenciados
- Recursos huérfanos
Ejecuta:
```
python vaultion_auditor.py
```

## 🛡️ Seguridad
- Cifrado con clave USB física
- Firma digital de claves
- Reparación automática de base de datos
- No se almacenan contraseñas en texto plano

## 🧩 Contribuciones
Este proyecto no acepta contribuciones externas sin autorización previa.
Para propuestas técnicas o licencias comerciales, contacta directamente con el autor.




