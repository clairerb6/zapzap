from PyQt6.QtCore import QStandardPaths, QFileInfo
try:
    import dbus
except ImportError:
    dbus = None
    print("Could not import dbus. Ensure 'python-dbus' is installed.")
import os
import sys


class AutostartManager:
    CONFIG_PATH = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.ConfigLocation) + '/autostart/com.rtosta.zapzap.desktop'
    IS_FLATPAK = QFileInfo(__file__).absolutePath().startswith('/app/')
    IS_WINDOWS = os.name == "nt"
    WINDOWS_STARTUP_FILE = "zapzap-autostart.cmd"

    @staticmethod
    def create_desktop_file(enable_autostart: bool):
        """Creates or removes the autostart desktop entry."""
        if AutostartManager.IS_WINDOWS:
            AutostartManager._handle_windows(enable_autostart)
        elif AutostartManager.IS_FLATPAK:
            AutostartManager._handle_flatpak(enable_autostart)
        else:
            AutostartManager._handle_local(enable_autostart)

    @staticmethod
    def _handle_flatpak(enable_autostart: bool):
        """Manages autostart settings for Flatpak installations."""
        if dbus is None:
            return
        try:
            bus = dbus.SessionBus()
            obj = bus.get_object("org.freedesktop.portal.Desktop",
                                 "/org/freedesktop/portal/desktop")
            interface = dbus.Interface(
                obj, "org.freedesktop.portal.Background")
            interface.RequestBackground('', {
                'reason': 'Zapzap autostart',
                'autostart': enable_autostart,
                'background': enable_autostart,
                'commandline': dbus.Array(['zapzap', '--hideStart'])
            })
        except Exception as e:
            print(f"Error managing Flatpak autostart: {e}")

    @staticmethod
    def _get_windows_startup_path() -> str:
        appdata = os.getenv("APPDATA", "")
        return os.path.join(
            appdata,
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs",
            "Startup",
            AutostartManager.WINDOWS_STARTUP_FILE
        )

    @staticmethod
    def _handle_windows(enable_autostart: bool):
        startup_file = AutostartManager._get_windows_startup_path()
        if enable_autostart:
            AutostartManager._create_windows_startup_file(startup_file)
        else:
            AutostartManager._remove_windows_startup_file(startup_file)

    @staticmethod
    def _create_windows_startup_file(path: str):
        exe = sys.executable
        if getattr(sys, "frozen", False):
            command = f'"{exe}" --hideStart'
        else:
            command = f'"{exe}" -m zapzap --hideStart'

        content = "@echo off\r\n" + f"start \"\" {command}\r\n"
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)
        except Exception as e:
            print(f"Error creating Windows startup file: {e}")

    @staticmethod
    def _remove_windows_startup_file(path: str):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"Error removing Windows startup file: {e}")

    @staticmethod
    def _handle_local(enable_autostart: bool):
        """Manages autostart settings for local installations."""
        if enable_autostart:
            AutostartManager._create_local_desktop_entry()
        else:
            AutostartManager._remove_local_desktop_entry()

    @staticmethod
    def _create_local_desktop_entry():
        """Creates a local autostart desktop entry."""
        desktop_entry_content = """[Desktop Entry]
Version=1.0
Name=ZapZap
Comment[pt_BR]=Whatsapp Desktop para Linux
Comment=Whatsapp Desktop for Linux
Exec=zapzap %u --hideStart
Icon=com.rtosta.zapzap
Type=Application
Categories=Chat;Network;InstantMessaging;Qt;
Keywords=Whatsapp;Chat;ZapZap;
StartupWMClass=ZapZap
MimeType=x-scheme-handler/whatsapp
Terminal=false
SingleMainWindow=true
X-GNOME-UsesNotifications=true
X-GNOME-SingleWindow=true"""

        try:
            with open(AutostartManager.CONFIG_PATH, 'w') as file:
                file.write(desktop_entry_content)
        except Exception as e:
            print(f"Error creating desktop entry: {e}")

    @staticmethod
    def _remove_local_desktop_entry():
        """Removes the local autostart desktop entry."""
        try:
            if os.path.exists(AutostartManager.CONFIG_PATH):
                os.remove(AutostartManager.CONFIG_PATH)
        except Exception as e:
            print(f"Error removing desktop entry: {e}")
