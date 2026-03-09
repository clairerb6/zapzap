from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QProcess, QUrl
from PyQt6.QtGui import QDesktopServices, QIcon
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from gettext import gettext as _
import os


class DownloadCompleteWidget(QWidget):
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.margin = 10
        self.setWindowFlags(
            QtCore.Qt.WindowType.Tool |
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self.setFocus()
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Maximum,
            QtWidgets.QSizePolicy.Policy.Maximum
        )

        self._build_ui()

        if self.parent():
            self.parent().installEventFilter(self)
        QtWidgets.QApplication.instance().installEventFilter(self)

        self.adjustSize()

    def _build_ui(self):
        container = QFrame(self)
        container.setFrameShape(QFrame.Shape.NoFrame)
        container.setObjectName("Container")

        title = QLabel(os.path.basename(self.file_path))
        title.setWordWrap(True)

        open_btn = QPushButton(_("Open"))
        open_btn.setIcon(QIcon.fromTheme("document-open"))
        open_btn.clicked.connect(self._open_file)

        folder_btn = QPushButton(_("Open folder"))
        folder_btn.setIcon(QIcon.fromTheme("folder-open"))
        folder_btn.clicked.connect(self._open_folder)

        buttons = QHBoxLayout()
        buttons.setSpacing(6)
        buttons.addWidget(open_btn)
        buttons.addWidget(folder_btn)

        content = QVBoxLayout(container)
        content.setSpacing(8)
        content.addWidget(title)
        content.addLayout(buttons)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)

        container.setStyleSheet(
            """
            #Container {
                background-color: palette(window);
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 10px;
            }
            """
        )

    def _reposition(self):
        if not self.parent():
            return

        rect = self.parent().rect()
        geo = self.frameGeometry()
        geo.moveBottomLeft(
            self.parent().mapToGlobal(rect.bottomLeft()) +
            QtCore.QPoint(self.margin, -self.margin)
        )
        self.setGeometry(geo)

    def eventFilter(self, source, event):
        if source == self.parent() and event.type() == QtCore.QEvent.Type.Resize:
            self._reposition()
        elif (
            source == QtWidgets.QApplication.instance()
            and event.type() == QtCore.QEvent.Type.MouseButtonPress
        ):
            global_pos = event.globalPosition().toPoint()
            if self.isVisible() and not self.frameGeometry().contains(global_pos):
                self.close()
        return super().eventFilter(source, event)

    def closeEvent(self, event):
        if self.parent():
            self.parent().removeEventFilter(self)
        app = QtWidgets.QApplication.instance()
        if app:
            app.removeEventFilter(self)
        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        self._reposition()
        self.raise_()
        self.activateWindow()

    def _open_file(self):
        if os.path.exists(self.file_path):
            self._open_local_path(self.file_path)
        self.close()

    def _open_folder(self):
        directory = os.path.dirname(self.file_path)
        if os.path.isdir(directory):
            self._open_local_path(directory)
        self.close()

    def _open_local_path(self, path: str):
        if QProcess.startDetached("xdg-open", [path]):
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
