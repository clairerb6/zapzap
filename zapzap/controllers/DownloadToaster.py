from PyQt6.QtCore import QFileInfo
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStyle,
    QVBoxLayout,
)
from gettext import gettext as _
import os

from zapzap.services.SettingsManager import SettingsManager


class DownloadToaster(QDialog):
    ACTION_CANCEL = "cancel"
    ACTION_OPEN = "open"
    ACTION_OPEN_FOLDER = "open_folder"
    ACTION_SAVE_AS = "save_as"

    def __init__(self, file_name: str, directory: str, parent=None):
        super().__init__(parent)
        self.file_name = file_name
        self.directory = directory
        self.selected_action = self.ACTION_CANCEL
        self.selected_path = None

        self.setModal(True)
        self.setWindowTitle(_("Download"))
        self.setWindowFlag(self.windowFlags() & ~self.windowFlags().WindowContextHelpButtonHint)

        self._build_ui()

    def _build_ui(self):
        container = QFrame(self)
        container.setFrameShape(QFrame.Shape.NoFrame)

        message = QLabel(_("Choose what to do with this download."))
        message.setWordWrap(True)

        title = QLabel(self.file_name)
        title.setWordWrap(True)

        open_btn = QPushButton(_("Open"))
        open_btn.setIcon(QIcon.fromTheme("document-open"))
        open_btn.clicked.connect(lambda: self._select_action(self.ACTION_OPEN))

        folder_btn = QPushButton(_("Open folder"))
        folder_btn.setIcon(QIcon.fromTheme("folder-open"))
        folder_btn.clicked.connect(
            lambda: self._select_action(self.ACTION_OPEN_FOLDER)
        )

        save_as_btn = QPushButton(_("Save as"))
        save_as_btn.setIcon(QIcon.fromTheme("document-save-as"))
        save_as_btn.clicked.connect(self._handle_save_as)

        cancel_btn = QPushButton(_("Cancel"))
        cancel_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)
        )
        cancel_btn.clicked.connect(self.reject)

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

        container.setStyleSheet(
            """
            QFrame {
                background-color: palette(window);
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 10px;
            }
            """
        )

    def _select_action(self, action: str):
        self.selected_action = action
        self.accept()

    def _handle_save_as(self):
        suffix = QFileInfo(self.file_name).suffix()
        options = (
            QFileDialog.Option.DontUseNativeDialog
            if SettingsManager.get("system/DontUseNativeDialog", False)
            else QFileDialog.Option(0)
        )

        path, __ = QFileDialog.getSaveFileName(
            self,
            _("Save file"),
            os.path.join(self.directory, self.file_name),
            f"*.{suffix}",
            options=options,
        )

        if not path:
            return

        self.selected_action = self.ACTION_SAVE_AS
        self.selected_path = path
        self.accept()
