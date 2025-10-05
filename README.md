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
- **VAULTION/ ├── main.py                  
- **Punto de entrada ├── vaultion_boot.py         
- **# Carga y verificación de clave USB ├── VaultDBManager.py        
- **# Acceso y reparación de base de datos ├── UnlockScreen.py          
- **# Pantalla de desbloqueo ├── AddEntryDialog.py        
- **# Diálogo para añadir entradas ├── KeyManagerWindow.py      
- **# Gestión visual de claves ├── SettingsWindow.py        
- **# Preferencias y mantenimiento ├── assets/                  
- **# Iconos y recursos gráficos ├── legacy/                  
- **# Módulos obsoletos (excluidos por .gitignore) └── LICENSE.txt              
- **# Licencia personalizada
