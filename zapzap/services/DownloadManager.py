from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import QStandardPaths
from gettext import gettext as _
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.DownloadNamingService import DownloadNamingService
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QFileDialog
from zapzap.controllers.DownloadCompleteWidget import DownloadCompleteWidget
from zapzap.controllers.DownloadDialog import DownloadDialog
import os


class DownloadManager:
    DOWNLOAD_PATH = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DownloadLocation
    )
    _completion_widgets = []
    _download_dialogs = []

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
        DownloadManager._set_web_toast_hidden(parent, True)

        def on_state_changed(state):
            cancelled = (
                QWebEngineDownloadRequest.DownloadState.DownloadCancelled,
                QWebEngineDownloadRequest.DownloadState.DownloadInterrupted
            )
            if state in cancelled:
                DownloadManager._set_web_toast_hidden(parent, False)
                return
            if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                DownloadManager._show_download_complete_widget(download, parent)

        download.stateChanged.connect(on_state_changed)

        DownloadManager._normalize_download_file_name(download)

        dialog = DownloadDialog(download, parent)
        DownloadManager._download_dialogs.append(dialog)
        dialog.destroyed.connect(
            lambda *_: DownloadManager._download_dialogs.remove(dialog)
            if dialog in DownloadManager._download_dialogs else None
        )
        dialog.show()

    @staticmethod
    def _normalize_download_file_name(download: QWebEngineDownloadRequest):
        file_name = DownloadNamingService.normalized_file_name(
            download.downloadFileName() or download.suggestedFileName(),
            download.mimeType(),
            download.url().toString()
        )

        if file_name != download.downloadFileName():
            download.setDownloadFileName(file_name)

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
            DownloadManager._set_web_toast_hidden(parent, False)
            return

        widget_parent = parent.window() if parent and parent.window() else parent

        def show_widget():
            widget = DownloadCompleteWidget(file_path, widget_parent)
            DownloadManager._completion_widgets.append(widget)
            widget.destroyed.connect(
                lambda *_: DownloadManager._completion_widgets.remove(widget)
                if widget in DownloadManager._completion_widgets else None
            )
            widget.destroyed.connect(
                lambda *_: DownloadManager._set_web_toast_hidden(parent, False)
            )
            widget.show()
            widget.raise_()

        QTimer.singleShot(0, show_widget)

    @staticmethod
    def _set_web_toast_hidden(parent, hidden: bool):
        if not parent or not hasattr(parent, "page") or not parent.page():
            return

        page = parent.page()
        count = page.property("zapzapHiddenToastCount") or 0

        if hidden:
            count += 1
            page.setProperty("zapzapHiddenToastCount", count)
            if count > 1:
                return
            script = """
            (function() {
              const styleId = 'zapzap-hide-wds-toast';
              if (document.getElementById(styleId)) return;
              const style = document.createElement('style');
              style.id = styleId;
              style.textContent = '#wds-toast-container { display: none !important; }';
              document.head.appendChild(style);
            })();
            """
        else:
            count = max(0, count - 1)
            page.setProperty("zapzapHiddenToastCount", count)
            if count > 0:
                return
            script = """
            (function() {
              const style = document.getElementById('zapzap-hide-wds-toast');
              if (style) style.remove();
            })();
            """

        try:
            page.runJavaScript(script)
        except Exception:
            pass
