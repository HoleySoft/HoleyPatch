# -*- coding: utf-8 -*-
from PySide2 import QtCore, QtGui, QtWidgets


def splash_screen(widget: QtWidgets.QMainWindow, obj: object) -> None:
    """Displays a splash screen ig it was set in the main object

    Parameters
    ----------
    widget : PySide2.QtWidgets.QMainWindow
        The main window widget to project the splash screen on
    obj : object
        The main PySential object containing required attributes

    Returns
    -------
    None
    """

    # Check if splash parameters are set
    if obj.splash:
        # Unpack the image location and text to display
        splash_img, a = obj.splash

        # Make a QPixMap from the file location
        splash_img = QtGui.QPixmap(splash_img)

        # Generate the splash screen and set it as a mask
        splash = QtWidgets.QSplashScreen(splash_img, QtCore.Qt.WindowStaysOnTopHint)
        splash.setMask(splash_img.mask())

        # Add the text to the splash screen
        splash.showMessage(a, alignment=QtCore.Qt.AlignRight, color=QtCore.Qt.white)

        # Show the splash screen and set the finish parameter
        splash.show()
        splash.finish(widget)
