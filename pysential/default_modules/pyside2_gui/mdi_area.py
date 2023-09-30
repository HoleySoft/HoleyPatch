# Import modules
from PySide2 import QtGui, QtCore
from PySide2.QtWidgets import QMdiArea


class MdiArea(QMdiArea):
    """A class used to load images from different file location(s) or packages.

    Attributes
    ----------
    img_bg : QtGui.QPixmap
        QPixMap of the background image
    img_scale : float
        Scaling factor
    width_height : float
        img_bg width over img_bg height
    height_width : float
        img_bg height over img_bg width

    Methods
    ----------
    paintEvent(event)
        Upon trigger, create background image rescaled
    """
    def __init__(self, parent=None, img=None, scale=0.8):
        QMdiArea.__init__(self, parent=parent)
        self.setBackground(QtGui.QBrush(QtCore.Qt.gray))
        self.img_bg = None
        self.img_scale = scale
        if img:
            self.img_bg = QtGui.QPixmap(img)
            self.width_height = self.img_bg.width() / self.img_bg.height()
            self.height_width = self.img_bg.height() / self.img_bg.width()

    def paintEvent(self, event):
        """Resize background image upon window size change

        Parameters
        ----------
        event
            Event trigger
        """
        if self.img_bg:
            QMdiArea.paintEvent(self, event)
            painter = QtGui.QPainter(self.viewport())
            window_width = self.rect().width()
            window_height = self.rect().height()
            aspect_ratio = max([self.img_bg.width() / window_width, self.img_bg.height() / window_height, 1])
            img_height = int(self.img_scale * self.img_bg.height() / aspect_ratio)
            img_width = int(self.img_scale * self.img_bg.width() / aspect_ratio)
            x_pos = int((window_width - img_width) / 2)
            y_pos = int((window_height - img_height) / 2)
            rect = QtCore.QRect(x_pos, y_pos, img_width, img_height)
            painter.drawPixmap(rect, self.img_bg)
