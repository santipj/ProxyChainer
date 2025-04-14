#!/usr/bin/env python3
import argparse
import configparser
import os
import subprocess
import sys
import socket
import socks
import re
import time
import requests

# Default configuration file path
DEFAULT_CONFIG_PATH = os.path.expanduser("~/.proxychainer.conf")

# Proxy types mapping
PROXY_TYPES = {
    "http": socks.HTTP,
    "socks4": socks.SOCKS4,
    "socks5": socks.SOCKS5
}

class ProxyChainer:
    def __init__(self, config_path=None, quiet=False):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.quiet = quiet
        self.proxies = []
        self.chain_type = "strict"
        self.load_config()

    def load_config(self):
        """Load proxy configuration from the config file"""
        if not os.path.exists(self.config_path):
            if not self.quiet:
                print(f"[!] Config file {self.config_path} not found. Creating default configuration.")
            self.create_default_config()

        config = configparser.ConfigParser()
        config.read(self.config_path)

        # Get chain type
        if "ProxyChainer" in config and "chain_type" in config["ProxyChainer"]:
            self.chain_type = config["ProxyChainer"]["chain_type"]

        # Get proxies
        if "ProxyList" in config:
            for key in config["ProxyList"]:
                match = re.match(r"(http|socks4|socks5)\s+([\w\.\-]+)\s+(\d+)", config["ProxyList"][key])
                if match:
                    proxy_type, host, port = match.groups()
                    self.proxies.append({
                        "type": proxy_type,
                        "host": host,
                        "port": int(port)
                    })

        if not self.proxies and not self.quiet:
            print("[!] No proxies found in the configuration file.")

    def create_default_config(self):
        """Create a default configuration file"""
        config = configparser.ConfigParser()
        config["ProxyChainer"] = {
            "chain_type": "strict",  # strict, dynamic, or random
            "quiet_mode": "off",
            "proxy_dns": "on"
        }

        config["ProxyList"] = {
            "proxy1": "socks5 127.0.0.1 9050",
            "proxy2": "http 192.168.1.1 8080"
        }

        os.makedirs(os.path.dirname(os.path.abspath(self.config_path)), exist_ok=True)
        with open(self.config_path, "w") as f:
            config.write(f)

        if not self.quiet:
            print(f"[+] Default configuration created at {self.config_path}")

    def setup_proxies(self):
        """Set up the proxy chain based on configuration"""
        if not self.proxies:
            if not self.quiet:
                print("[!] No proxies configured. Running command directly.")
            return False

        first_proxy = self.proxies[0]
        if first_proxy["type"] == "socks5" and first_proxy["host"] == "127.0.0.1" and first_proxy["port"] == 9050:
            if self.change_tor_identity():
                print("[+] Tor identity changed before applying proxy.")
                self.show_current_ip()

        socks.set_default_proxy(
            PROXY_TYPES.get(first_proxy["type"], socks.SOCKS5),
            first_proxy["host"],
            first_proxy["port"]
        )
        socket.socket = socks.socksocket

        return True

    def change_tor_identity(self):
        """Sends NEWNYM signal to Tor for a new identity"""
        try:
            with socket.create_connection(("127.0.0.1", 9051)) as s:
                s.sendall(b'AUTHENTICATE \"\"\r\n')
                response = s.recv(1024).decode()
                if "250 OK" not in response:
                    print("[!] Failed to authenticate with Tor control port. Check torrc settings.")
                    return False

                s.sendall(b'SIGNAL NEWNYM\r\n')
                response = s.recv(1024).decode()
                if "250 OK" in response:
                    print("[+] Tor identity changed successfully.")
                    self.show_current_ip()
                    return True
                else:
                    print("[!] Failed to change Tor identity.")
                    return False
        except Exception as e:
            print(f"[!] Error changing Tor identity: {e}")
            return False

    def show_current_ip(self):
        """Fetch and display the current public IP address"""
        try:
            ip = requests.get("https://check.torproject.org/api/ip", proxies={"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}).json()["IP"]
            print(f"[+] Current IP: {ip}")
        except Exception as e:
            print(f"[!] Failed to retrieve IP: {e}")

    def run_command(self, command):
        """Run a command through the proxy chain"""
        if not self.setup_proxies():
            return subprocess.call(command)

        if not self.quiet:
            print(f"[+] Running command through proxy: {' '.join(command)}")

        return subprocess.call(command)


def validate_torrc():
    """Verifica si la configuración necesaria está presente en torrc y la aplica si falta."""
    possible_paths = [
        "/etc/tor/torrc",  # Linux (requiere sudo)
        os.path.expanduser("~/.torrc"),  # Usuario local en Linux/macOS
        f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\tor\\torrc"  # Windows
    ]

    torrc_path = None
    for path in possible_paths:
        if os.path.exists(path):
            torrc_path = path
            break

    if not torrc_path:
        print("[!] No se encontró el archivo torrc. Asegúrate de que Tor esté instalado.")
        return False

    # Configuraciones requeridas
    required_settings = {
        "ControlPort": "9051",
        "DNSPort": "53",
        "AutomapHostsOnResolve": "1",
        "CookieAuthentication": "0"
    }

    # Leer y analizar el archivo torrc
    with open(torrc_path, "r") as f:
        lines = f.readlines()

    modified = False
    new_lines = []
    
    for line in lines:
        stripped = line.strip()
        found = False

        for key, value in required_settings.items():
            if stripped.startswith(key):  # Si la línea ya tiene una de las configuraciones
                current_value = stripped.split(" ", 1)[1] if " " in stripped else ""
                if current_value != value:
                    print(f"[!] Corrigiendo {key}: {current_value} -> {value}")
                    new_lines.append(f"{key} {value}\n")  # Corrige la línea
                    modified = True
                else:
                    new_lines.append(line)  # Mantiene la línea si es correcta
                found = True
                break

        if not found:
            new_lines.append(line)  # Mantiene líneas no relacionadas

    # Agregar configuraciones que falten
    for key, value in required_settings.items():
        if not any(line.startswith(f"{key} ") for line in new_lines):
            print(f"[+] Agregando {key} {value}")
            new_lines.append(f"{key} {value}\n")
            modified = True

    # Guardar cambios si hubo modificaciones
    if modified:
        with open(torrc_path, "w") as f:
            f.writelines(new_lines)
        
        print(f"[+] Se ha actualizado la configuración en {torrc_path}. Es necesario reiniciar Tor.")

        # Intentar reiniciar Tor automáticamente
        try:
            subprocess.run(["systemctl", "restart", "tor"], check=True)
            print("[+] Tor ha sido reiniciado correctamente.")
        except Exception as e:
            print(f"[!] No se pudo reiniciar Tor automáticamente: {e}. Reinícialo manualmente.")
    else:
        print("[+] La configuración de Tor ya está correcta.")

    return True



def main():
    if validate_torrc():
        proxy_chainer = ProxyChainer()

        interval = int(input("Ingrese el intervalo (en segundos) para cambiar la identidad de Tor: "))

        while True:
            proxy_chainer.change_tor_identity()
            time.sleep(interval)  # Espera el tiempo definido antes de cambiar nuevamente



if __name__ == "__main__":
    if validate_torrc():
        sys.exit(main())
    else:
        print("[!] No se pudo validar la configuración de Tor. Saliendo...")
        sys.exit(1)

