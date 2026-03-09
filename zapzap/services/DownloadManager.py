from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import QStandardPaths
from gettext import gettext as _
from zapzap.services.SettingsManager import SettingsManager
from PyQt6.QtWidgets import QFileDialog

from zapzap.controllers.DownloadToaster import DownloadToaster
from gettext import gettext as _


class DownloadManager:
    DOWNLOAD_PATH = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DownloadLocation
    )

    _floating_cards = []

    @staticmethod
    def set_path(new_path):
        SettingsManager.set("system/download_path", new_path)

    @staticmethod
    def get_path():
        return SettingsManager.get(
            "system/download_path",
            DownloadManager.DOWNLOAD_PATH
        )

    @staticmethod
    def restore_path():
        SettingsManager.set(
            "system/download_path",
            DownloadManager.DOWNLOAD_PATH
        )

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
        DownloadManager._floating_cards.append(toaster)
        toaster.destroyed.connect(
            lambda *_: DownloadManager._floating_cards.remove(toaster)
            if toaster in DownloadManager._floating_cards else None
        )
        toaster.open()

    @staticmethod
    def open_folder_dialog(parent):
        directory = DownloadManager.get_path()

        options = (
            QFileDialog.Option.DontUseNativeDialog
            if SettingsManager.get("system/DontUseNativeDialog", False)
            else QFileDialog.Option(0)
        )

        folder_path = QFileDialog.getExistingDirectory(
            parent=parent,
            caption=_("Select folder"),
            directory=directory,
            options=options
        )

        return folder_path or None
