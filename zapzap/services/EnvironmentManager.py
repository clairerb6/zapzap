import os
import sys
from enum import Enum


class Packaging(Enum):
    APPIMAGE = "AppImage"
    FLATPAK = "Flatpak"
    RPM = "RPM"
    DEB = "DEB"
    UNOFFICIAL = "Unofficial"
    WINDOWS = "Windows"


class EnvironmentManager:
    @staticmethod
    def identify_distribution() -> str:
        """Identifies Linux distribution using /etc/os-release."""
        os_release_path = "/etc/os-release"
        if not os.path.exists(os_release_path):
            return ""

        values = {}
        try:
            with open(os_release_path, "r", encoding="utf-8") as os_release_file:
                for line in os_release_file:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    values[key] = value.strip().strip('"')
        except OSError:
            return ""

        if values.get("PRETTY_NAME"):
            return values["PRETTY_NAME"]

        name = values.get("NAME", "").strip()
        version = values.get("VERSION_ID", "").strip()
        if name and version:
            return f"{name} {version}"

        return name

    @staticmethod
    def _detect_system_packaging(app_path: str):
        """Detects system package format (DEB/RPM) for binaries in standard paths."""
        if not (app_path.startswith("/usr/bin/") or app_path.startswith("/usr/local/bin/")):
            return Packaging.UNOFFICIAL

        # Debian/Ubuntu and derivatives
        if os.path.exists("/etc/debian_version") or os.path.exists("/var/lib/dpkg/status"):
            return Packaging.DEB

        # Fedora/RHEL/openSUSE and derivatives
        if os.path.exists("/var/lib/rpm") or os.path.exists("/usr/bin/rpm"):
            return Packaging.RPM

        return Packaging.UNOFFICIAL

    @staticmethod
    def identify_packaging():
        """Identifies the packaging type of the application and returns an Enum."""

        if sys.platform == "win32":
            return Packaging.WINDOWS

        if "APPIMAGE" in os.environ:
            return Packaging.APPIMAGE
        elif "FLATPAK_ID" in os.environ:
            return Packaging.FLATPAK

        # Identification via executable path
        app_path = os.path.abspath(sys.argv[0])

        return EnvironmentManager._detect_system_packaging(app_path)

    @staticmethod
    def show_information():
        """Displays information about the identified packaging."""
        packaging = EnvironmentManager.identify_packaging()
        print(f"Empacotamento identificado: {packaging.value}")

        if packaging == Packaging.APPIMAGE:
            appdir = os.getenv("APPDIR", "")
            if appdir:
                print(f"Diretório do AppImage: {appdir}")
                print(f"Arquivos no diretório: {os.listdir(appdir)}")

    @staticmethod
    def isOfficial() -> bool:
        # Official upstream channels.
        return EnvironmentManager.identify_packaging() in {Packaging.APPIMAGE, Packaging.FLATPAK}
