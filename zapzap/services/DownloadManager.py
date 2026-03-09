from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import QStandardPaths
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from gettext import gettext as _
from zapzap.services.SettingsManager import SettingsManager
from PyQt6.QtWidgets import QFileDialog
from zapzap.controllers.DownloadToaster import DownloadToaster
import os
import shutil


class DownloadManager:
    DOWNLOAD_PATH = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DownloadLocation
    )

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

        dialog = DownloadToaster(
            download.downloadFileName(),
            download.downloadDirectory(),
            parent
        )
        result = dialog.exec()

        if result != dialog.DialogCode.Accepted:
            download.cancel()
            return

        action = dialog.selected_action
        if action == DownloadToaster.ACTION_CANCEL:
            download.cancel()
            return

        if action == DownloadToaster.ACTION_SAVE_AS and dialog.selected_path:
            requested_dir = os.path.dirname(dialog.selected_path)
            requested_name = os.path.basename(dialog.selected_path)
            download.setDownloadDirectory(requested_dir)
            download.setDownloadFileName(requested_name)

            current_dir = download.downloadDirectory()
            current_name = download.downloadFileName()
            if current_dir != requested_dir or current_name != requested_name:
                def move_when_done(state):
                    if state != QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                        return
                    try:
                        source = os.path.join(current_dir, current_name)
                        if os.path.exists(source):
                            os.makedirs(requested_dir, exist_ok=True)
                            shutil.move(source, dialog.selected_path)
                    except Exception:
                        pass

                download.stateChanged.connect(move_when_done)

        if action == DownloadToaster.ACTION_OPEN:
            download.stateChanged.connect(
                lambda state: DownloadManager._open_when_done(download, state)
            )
        elif action == DownloadToaster.ACTION_OPEN_FOLDER:
            download.stateChanged.connect(
                lambda state: DownloadManager._open_folder_when_done(download, state)
            )

        download.accept()

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

    @staticmethod
    def _open_when_done(download, state):
        if state != QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            return
        path = os.path.join(
            download.downloadDirectory(),
            download.downloadFileName()
        )
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    @staticmethod
    def _open_folder_when_done(download, state):
        if state != QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            return
        directory = download.downloadDirectory()
        if os.path.isdir(directory):
            QDesktopServices.openUrl(QUrl.fromLocalFile(directory))
