from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from zapzap.services.SysTrayManager import SysTrayManager


class WindowsNotificationBackend:
    """Simple notification backend for Windows using Qt system tray."""

    def available(self) -> bool:
        return QSystemTrayIcon.isSystemTrayAvailable()

    def notify(self, page, notification, title: str, message: str):
        app = QApplication.instance()
        if not app:
            return

        tray = None
        try:
            tray = SysTrayManager.instance()._tray
        except Exception:
            tray = None

        if tray:
            tray.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                6000
            )
            return

        try:
            notification.show()
        except Exception:
            pass
