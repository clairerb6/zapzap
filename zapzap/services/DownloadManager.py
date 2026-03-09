from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import QStandardPaths
from gettext import gettext as _
from zapzap.services.SettingsManager import SettingsManager
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QFileDialog
from zapzap.controllers.DownloadCompleteWidget import DownloadCompleteWidget
from zapzap.controllers.DownloadDialog import DownloadDialog
import os
import shutil


class DownloadManager:
    DOWNLOAD_PATH = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DownloadLocation
    )
    _completion_widgets = []

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
            if state in cancelled:
                return
            if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                DownloadManager._show_download_complete_widget(download, parent)

        download.stateChanged.connect(on_state_changed)

        dialog = DownloadDialog(
            download.downloadFileName(),
            download.downloadDirectory(),
            parent
        )
        result = dialog.exec()

        if result != dialog.DialogCode.Accepted:
            download.cancel()
            return

        action = dialog.selected_action
        if action == DownloadDialog.ACTION_CANCEL:
            download.cancel()
            return

        if action == DownloadDialog.ACTION_SAVE_AS and dialog.selected_path:
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
    def _show_download_complete_widget(download, parent):
        file_path = os.path.join(
            download.downloadDirectory(),
            download.downloadFileName()
        )
        if not os.path.exists(file_path):
            return

        widget_parent = parent.window() if parent and parent.window() else parent

        def show_widget():
            widget = DownloadCompleteWidget(file_path, widget_parent)
            DownloadManager._completion_widgets.append(widget)
            widget.destroyed.connect(
                lambda *_: DownloadManager._completion_widgets.remove(widget)
                if widget in DownloadManager._completion_widgets else None
            )
            widget.show()
            widget.raise_()
            widget.activateWindow()

        QTimer.singleShot(0, show_widget)
