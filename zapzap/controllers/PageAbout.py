from gettext import gettext as _

from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QWidget

from zapzap import __appname__, __bugreport__, __donationPage__, __version__, __website__
from zapzap.resources.UserIcon import UserIcon
from zapzap.services.EnvironmentDetector import EnvironmentDetector
from zapzap.services.EnvironmentManager import EnvironmentManager
from zapzap.views.ui_page_about import Ui_PageAbout


class PageAbout(QWidget, Ui_PageAbout):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._setup_ui()
        self._configure_signals()

    def _setup_ui(self):
        self.icon.setIcon(UserIcon.get_icon())
        self.name_app.setText(__appname__)

        version_lines = [
            _(self.version_app.text()).format(id=__version__),
            _("Package: {package}").format(
                package=EnvironmentManager.identify_packaging().value
            ),
        ]

        distro = EnvironmentManager.identify_distribution()
        if distro:
            version_lines.append(distro)

        self.version_app.setText("\n".join(version_lines))
        self.qt_version.setText(f"Qt:{QT_VERSION_STR} - PyQt:{PYQT_VERSION_STR}")

        self._set_value_label(self.labelBuildChannel, _(EnvironmentDetector.CHANNEL))
        self._set_value_label(self.labelBuildProvider, _(EnvironmentDetector.PROVIDER))
        self._set_value_label(
            self.labelBuildRepository,
            _(EnvironmentDetector.BUILD_REPOSITORY),
        )

    def _set_value_label(self, label, value):
        label.setText(_(label.text()).format(value=value))

    def _configure_signals(self):
        self.btnLeanMore.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(__website__))
        )
        self.btnReportIssue.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(__bugreport__))
        )
        self.btnDonate.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(__donationPage__))
        )
