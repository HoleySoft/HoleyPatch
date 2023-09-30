# -*- coding: utf-8 -*-
# System default libraries
import sys

# Third party libraries
from PySide2 import QtWidgets

# Custom libraries
from .main import *
from .splash_screen import *
from .widgets import *
from .dialogs import *


__title__ = "Protolyse"
__author__ = "Florian L. R. Lucas"
__copyright__ = "Copyright 2020, Protolyse (TM)"
__license__ = "GPL"
__version__ = "0.0.1.0"
__maintainer__ = "Protolyse (TM)"
__email__ = "info@protolyse.com"
__status__ = "Prototype"


def run(obj: object) -> None:
    """Initialize GUI

    Parameters
    ----------
    obj : object
        Parent object

    Returns
    -------
    None
    """
    app = QtWidgets.QApplication(sys.argv)
    ex = Main(obj)
    _main(ex, app, obj)


def _main(ex, app, obj) -> None:
    """"Start the splash screen and subsequently the UI
    """
    # Start a splash screen if it was set in the main object
    splash_screen(ex, obj)
    ex.show_ui()
    sys.exit(app.exec_())
