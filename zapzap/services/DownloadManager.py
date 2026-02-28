from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import QStandardPaths
from gettext import gettext as _
from zapzap.services.SettingsManager import SettingsManager
from PyQt6.QtCore import Qt, QPoint

from zapzap.controllers.DownloadToaster import DownloadToaster


class DownloadManager:
    DOWNLOAD_PATH = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DownloadLocation
    )

    @staticmethod
    def get_path():
        return SettingsManager.get(
            "system/download_path",
            DownloadManager.DOWNLOAD_PATH
        )

    _floating_cards = []

    @staticmethod
    def on_downloadRequested(
        download: QWebEngineDownloadRequest,
        parent=None
    ):
        if download.state() != QWebEngineDownloadRequest.DownloadState.DownloadRequested:
            return

        download.setDownloadDirectory(
            DownloadManager.get_path()
        )

        # QtWebEngine destroys non-accepted requests after this callback returns.
        # Accept first to keep the request alive, then pause until user action.
        download.accept()
        download.pause()

        def on_state_changed(state):
            cancelled = (
                QWebEngineDownloadRequest.DownloadState.DownloadCancelled,
                QWebEngineDownloadRequest.DownloadState.DownloadInterrupted
            )
            if state in cancelled and parent and hasattr(parent, "page") and parent.page():
                try:
                    parent.page().show_toast(_("Download canceled"), 1600)
                except Exception:
                    pass

        download.stateChanged.connect(on_state_changed)

        toaster = DownloadToaster(download, parent)
        toaster.show()
