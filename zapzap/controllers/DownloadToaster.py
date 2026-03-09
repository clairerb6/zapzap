from PyQt6.QtWidgets import (
    QDialog, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QStyle, QFrame, QFileDialog
)
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QDesktopServices, QIcon, QCloseEvent
from PyQt6.QtCore import QUrl, QFileInfo
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from gettext import gettext as _
import os
import shutil

from zapzap.services.SettingsManager import SettingsManager


class DownloadToaster(QDialog):
    """
    Download toaster aligned with QtoasterDonation pattern.
    Top-right, solid background, floating inside the app.
    """

    def __init__(self, download: QWebEngineDownloadRequest, parent=None):
        super().__init__(parent)

        self.download = download
        self._cancelled = False
        self._download_started = False
        self._open_file_after_download = False
        self._open_folder_after_download = False

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Maximum,
            QtWidgets.QSizePolicy.Policy.Maximum
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setModal(True)
        self.setWindowTitle(_("Download"))
        self.setWindowFlag(QtCore.Qt.WindowType.WindowContextHelpButtonHint, False)

        self._build_ui()
        self.download.stateChanged.connect(self._handle_download_state_changed)

    # ===============================
    # UI
    # ===============================

    def _build_ui(self):
        self.setObjectName("DownloadToaster")

        container = QFrame(self)
        container.setObjectName("Container")
        container.setFrameShape(QFrame.Shape.NoFrame)

        message = QLabel(_("Choose what to do with this download."))
        message.setWordWrap(True)

        title = QLabel(self.download.downloadFileName())
        title.setWordWrap(True)

        open_btn = QPushButton(_("Open"))
        open_btn.setIcon(QIcon.fromTheme("document-open"))

        folder_btn = QPushButton(_("Open folder"))
        folder_btn.setIcon(QIcon.fromTheme("folder-open"))

        save_as_btn = QPushButton(_("Save as"))
        save_as_btn.setIcon(QIcon.fromTheme("document-save-as"))

        cancel_btn = QPushButton(_("Cancel"))
        cancel_btn.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_DialogCancelButton
            )
        )

        open_btn.clicked.connect(self._open_file)
        folder_btn.clicked.connect(self._open_folder)
        save_as_btn.clicked.connect(self._save_as)
        cancel_btn.clicked.connect(self._cancel)

        buttons = QHBoxLayout()
        buttons.setSpacing(6)
        buttons.addWidget(open_btn)
        buttons.addWidget(folder_btn)
        buttons.addWidget(save_as_btn)
        buttons.addWidget(cancel_btn)

        content = QVBoxLayout(container)
        content.setSpacing(8)
        content.addWidget(message)
        content.addWidget(title)
        content.addLayout(buttons)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.addWidget(container)

        container.setStyleSheet("""
            #Container {
                background-color: palette(window);
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 10px;
            }
        """)

    # ===============================
    # Actions
    # ===============================
    def _resume_download(self):
        try:
            if hasattr(self.download, "isPaused") and self.download.isPaused():
                self.download.resume()
                self._download_started = True
            elif self.download.state() == QWebEngineDownloadRequest.DownloadState.DownloadRequested:
                self.download.accept()
                self._download_started = True
        except RuntimeError:
            return

    def _open_file(self):
        try:
            if self._is_download_completed():
                self._open_downloaded_file()
                self.close()
            else:
                self._open_file_after_download = True
                self._resume_download()
        except RuntimeError:
            return

    def _open_folder(self):
        try:
            if self._is_download_completed():
                self._open_download_folder()
                self.close()
            else:
                self._open_folder_after_download = True
                self._resume_download()
        except RuntimeError:
            return

    def _save_as(self):
        """
        Reutiliza a lógica original de save_download
        """

        try:
            directory = self.download.downloadDirectory()
            file_name = self.download.downloadFileName()
        except RuntimeError:
            return
        suffix = QFileInfo(file_name).suffix()

        options = (
            QFileDialog.Option.DontUseNativeDialog
            if SettingsManager.get("system/DontUseNativeDialog", False)
            else QFileDialog.Option(0)
        )

        path, __ = QFileDialog.getSaveFileName(
            self,
            _("Save file"),
            os.path.join(directory, file_name),
            f"*.{suffix}",
            options=options
        )

        if not path:
            return

        try:
            requested_dir = os.path.dirname(path)
            requested_name = os.path.basename(path)

            self.download.setDownloadDirectory(requested_dir)
            self.download.setDownloadFileName(requested_name)

            # If Qt ignores destination changes after accept(), move on completion.
            current_dir = self.download.downloadDirectory()
            current_name = self.download.downloadFileName()
            if current_dir != requested_dir or current_name != requested_name:
                def move_when_done(state):
                    if state != QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                        return
                    try:
                        source = os.path.join(current_dir, current_name)
                        if os.path.exists(source):
                            os.makedirs(requested_dir, exist_ok=True)
                            shutil.move(source, path)
                    except Exception:
                        pass

                self.download.stateChanged.connect(move_when_done)

            self._resume_download()
        except RuntimeError:
            return

    def _cancel(self):
        self._cancelled = True
        try:
            self.download.cancel()
        except RuntimeError:
            # The underlying Qt download request may already be destroyed.
            pass
        self.close()

    def closeEvent(self, event: QCloseEvent):
        self._resume_if_pending()
        super().closeEvent(event)

    def _resume_if_pending(self):
        if self._cancelled or self._download_started:
            return
        self._resume_download()

    def _has_pending_open_action(self):
        return self._open_file_after_download or self._open_folder_after_download

    def _handle_download_state_changed(self, state):
        if state != QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            return
        if self._open_file_after_download:
            self._open_file_after_download = False
            self._open_downloaded_file()
        if self._open_folder_after_download:
            self._open_folder_after_download = False
            self._open_download_folder()
        if not self._open_file_after_download and not self._open_folder_after_download:
            self.close()

    def _is_download_completed(self):
        return (
            self.download.state()
            == QWebEngineDownloadRequest.DownloadState.DownloadCompleted
        )

    def _open_downloaded_file(self):
        path = os.path.join(
            self.download.downloadDirectory(),
            self.download.downloadFileName()
        )
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _open_download_folder(self):
        directory = self.download.downloadDirectory()
        if os.path.isdir(directory):
            QDesktopServices.openUrl(QUrl.fromLocalFile(directory))
