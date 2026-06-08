from PyQt6.QtCore import QFileInfo, Qt, QUrl
from PyQt6.QtGui import QAction, QDesktopServices, QIcon
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QStyle,
    QToolButton,
    QVBoxLayout,
)
from gettext import gettext as _
import os

from zapzap.services.DownloadNamingService import DownloadNamingService
from zapzap.services.SettingsManager import SettingsManager


class DownloadDialog(QDialog):
    def __init__(self, download: QWebEngineDownloadRequest, parent=None):
        super().__init__(parent)
        self.download = download
        self._handled = False

        self.setModal(True)
        self.setWindowTitle(_("Download"))
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMinimumWidth(420)

        self._build_ui()

    def _build_ui(self):
        container = QFrame(self)
        container.setObjectName("Container")

        title = QLabel(self.download.downloadFileName())
        title.setWordWrap(True)
        title.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        font = title.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 1)
        title.setFont(font)

        directory = QLabel(self.download.downloadDirectory())
        directory.setWordWrap(True)
        directory.setObjectName("Directory")
        directory.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        save_btn = QPushButton(_("Save"))
        save_btn.setIcon(
            QIcon.fromTheme(
                "document-save",
                self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton),
            )
        )
        save_btn.setDefault(True)
        save_btn.setAutoDefault(True)

        open_btn = QPushButton(_("Open"))
        open_btn.setIcon(
            QIcon.fromTheme(
                "document-open",
                self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton),
            )
        )

        more_btn = QToolButton()
        more_btn.setText(_("More"))
        more_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        menu = QMenu(self)
        save_as_action = QAction(QIcon.fromTheme("document-save-as"), _("Save as"), self)
        folder_action = QAction(QIcon.fromTheme("folder-open"), _("Open folder"), self)
        cancel_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton),
            _("Cancel"),
            self,
        )

        save_as_action.triggered.connect(self._save_as)
        folder_action.triggered.connect(self._open_folder)
        cancel_action.triggered.connect(self._cancel)

        menu.addAction(save_as_action)
        menu.addAction(folder_action)
        menu.addSeparator()
        menu.addAction(cancel_action)
        more_btn.setMenu(menu)

        save_btn.clicked.connect(self._save)
        open_btn.clicked.connect(self._open_file)

        buttons = QHBoxLayout()
        buttons.setSpacing(6)
        buttons.addStretch()
        buttons.addWidget(save_btn)
        buttons.addWidget(open_btn)
        buttons.addWidget(more_btn)

        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(directory)
        layout.addLayout(buttons)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)

        self.setStyleSheet(
            """
            #Container {
                background-color: palette(window);
                border-radius: 10px;
                padding: 14px;
            }

            QToolButton {
                padding: 5px 10px;
                font-size: 14px;
                border-radius: 6px;
            }
            """
        )

    def _open_file(self):
        directory = self.download.downloadDirectory()

        def open_when_done(state):
            if state != QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                return

            path = os.path.join(directory, self.download.downloadFileName())
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

        self.download.stateChanged.connect(open_when_done)
        self._save()

    def _open_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.download.downloadDirectory()))

    def _save(self):
        self._handled = True
        self.download.accept()
        self.close()

    def _save_as(self):
        directory = self.download.downloadDirectory()
        file_name = self.download.downloadFileName()
        suffix = QFileInfo(file_name).suffix()

        options = (
            QFileDialog.Option.DontUseNativeDialog
            if SettingsManager.get("system/DontUseNativeDialog", False)
            else QFileDialog.Option(0)
        )
        name_filter = f"*.{suffix}" if suffix else "*"

        path, __ = QFileDialog.getSaveFileName(
            self,
            _("Save file"),
            os.path.join(directory, file_name),
            name_filter,
            options=options,
        )

        if not path:
            return

        normalized_file_name = DownloadNamingService.normalized_file_name(
            os.path.basename(path),
            self.download.mimeType(),
            self.download.url().toString(),
        )

        self.download.setDownloadDirectory(os.path.dirname(path))
        self.download.setDownloadFileName(normalized_file_name)
        self._save()

    def _cancel(self):
        self._handled = True
        self.download.cancel()
        self.close()

    def closeEvent(self, event):
        if not self._handled:
            self.download.cancel()
            self._handled = True
        super().closeEvent(event)
