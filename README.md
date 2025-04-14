# 🔗 ProxyChainer - Herramienta Avanzada de Encadenamiento de Proxies

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

ProxyChainer es una herramienta Python para encadenar múltiples proxies de diferentes tipos (HTTP, SOCKS4, SOCKS5) y ejecutar comandos a través de ellos. Incluye funcionalidad especial para integración con Tor y cambio automático de identidad.

## ✨ Características Principales

- ✅ Soporte para múltiples tipos de proxy (HTTP, SOCKS4, SOCKS5)
- 🔄 Tres modos de encadenamiento: estricto, dinámico y aleatorio
- 🕵️‍♂️ Integración con Tor (cambio de identidad automático)
- 📝 Configuración mediante archivo fácil de editar
- 🌐 Verificación de IP actual
- ⚡ Ejecución de comandos a través de la cadena de proxies
- 🔄 Validación y configuración automática de torrc

## 🚀 Instalación Rápida

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/tuusuario/proxychainer.git
   cd proxychainer
   
2. **Instala las dependencias:**
   ```bash
   pip install pysocks requests configparser

2. **Configura Tor (opcional, solo si quieres usar Tor):**
   ```bash
   sudo apt install tor  # Para Debian/Ubuntu
   brew install tor     # Para macOS

⚙️ Configuración
El archivo de configuración por defecto se crea automáticamente en ~/.proxychainer.conf con este formato:
  ```bash
  [ProxyChainer]
  chain_type = strict  # strict, dynamic, or random
  quiet_mode = off
  proxy_dns = on
  
  [ProxyList]
  proxy1 = socks5 127.0.0.1 9050
  proxy2 = http 192.168.1.1 8080
  ```

🛠 Uso Básico
Ejecutar un comando a través de los proxies:
```bash
  python3 proxychainer.py --command "curl ifconfig.me"
  ```

Cambiar identidad de Tor manualmente:
```bash
  python3 proxychainer.py --new-tor-identity
  ```

Modo interactivo con intervalo de cambio automático:
```bash
  python3 proxychainer.py --interactive
  ```

📌 Opciones Disponibles
Opción	Descripción
--config	Ruta al archivo de configuración personalizado
--quiet	Modo silencioso (sin salida)
--command	Comando a ejecutar a través de los proxies
--new-tor-identity	Cambia la identidad de Tor
--interactive	Modo interactivo con cambio periódico
🔄 Modos de Encadenamiento
Strict Chain: Los proxies se usan en orden secuencial estricto

Dynamic Chain: Selección inteligente basada en rendimiento

Random Chain: Selección aleatoria de proxies

🤝 Contribuciones
¡Contribuciones son bienvenidas! Por favor abre un issue o envía un PR para:

Reportar bugs

Sugerir mejoras

Añadir nuevas funcionalidades

📜 Licencia
MIT - Ver LICENSE para más detalles.
