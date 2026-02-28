from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QStyle, QFrame, QFileDialog
)
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QDesktopServices, QIcon
from PyQt6.QtCore import QUrl, QFileInfo
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from gettext import gettext as _
import os
import shutil

from zapzap.services.SettingsManager import SettingsManager


class DownloadToaster(QWidget):
    """
    Download toaster aligned with QtoasterDonation pattern.
    Top-right, solid background, floating inside the app.
    """

    def __init__(self, download: QWebEngineDownloadRequest, parent=None):
        super().__init__(parent)

        self.download = download
        self.margin = 10

        self.setFocus()
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Maximum,
            QtWidgets.QSizePolicy.Policy.Maximum
        )

        self._build_ui()

        if self.parent():
            self.parent().installEventFilter(self)

        self.raise_()
        self.adjustSize()
        self._reposition()

    # ===============================
    # UI
    # ===============================

    def _build_ui(self):
        self.setObjectName("DownloadToaster")

        container = QFrame(self)
        container.setObjectName("Container")
        container.setFrameShape(QFrame.Shape.NoFrame)

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
        content.addWidget(title)
        content.addLayout(buttons)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
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
    # Positioning
    # ===============================

    def _reposition(self):
        if not self.parent():
            return

        rect = self.parent().rect()
        geo = self.geometry()
        geo.moveBottomLeft(
            rect.bottomLeft() +
            QtCore.QPoint(self.margin+65, -self.margin)
        )
        self.setGeometry(geo)

    def eventFilter(self, source, event):
        if source == self.parent() and event.type() == QtCore.QEvent.Type.Resize:
            self._reposition()
        return super().eventFilter(source, event)

    # ===============================
    # Actions
    # ===============================
    def _resume_download(self):
        try:
            if hasattr(self.download, "isPaused") and self.download.isPaused():
                self.download.resume()
            elif self.download.state() == QWebEngineDownloadRequest.DownloadState.DownloadRequested:
                self.download.accept()
        except RuntimeError:
            return

    def _open_file(self):
        try:
            directory = self.download.downloadDirectory()
            self._resume_download()
        except RuntimeError:
            return

        def open_when_done(state):
            if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                path = os.path.join(
                    directory,
                    self.download.downloadFileName()
                )
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))

        self.download.stateChanged.connect(open_when_done)

    def _open_folder(self):
        try:
            directory = self.download.downloadDirectory()
            self._resume_download()
        except RuntimeError:
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(directory))

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
        try:
            self.download.cancel()
        except RuntimeError:
            # The underlying Qt download request may already be destroyed.
            pass
        self.close()

    # ===============================
    # Focus behavior
    # ===============================

    def focusOutEvent(self, event):
        self.close()
