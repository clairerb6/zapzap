from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

from zapzap.resources.UserIcon import UserIcon
from zapzap.services.EnvironmentManager import EnvironmentManager
from zapzap.views.ui_page_about import Ui_PageAbout
from zapzap import __bugreport__, __featurerequest__, __website__, __version__

from gettext import gettext as _


class PageAbout(QWidget, Ui_PageAbout):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.icon.setIcon(UserIcon.get_icon())

        v_type = _("Official compilation") if EnvironmentManager.isOfficial() else _(
            """Unofficial""")

        v_package = EnvironmentManager.identify_packaging().value
        distro = EnvironmentManager.identify_distribution()

        version_text = _(self.version_app.text()).format(
            id=__version__,
            version_type=v_type,
            package=v_package
        )

        if distro:
            version_text = f"{version_text}\n{distro}"

        self.version_app.setText(version_text)

        self.btnLeanMore.clicked.connect(
            lambda:  QDesktopServices.openUrl(QUrl(__website__)))

        self.btnReportIssue.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(__bugreport__)))

        self.btnFeatureRequest.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(__featurerequest__)))
