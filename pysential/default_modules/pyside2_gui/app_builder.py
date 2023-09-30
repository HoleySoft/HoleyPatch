
from PySide2 import QtGui, QtCore
from PySide2 import QtWidgets


class AppBuilder(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AppBuilder, self).__init__(parent)
        layout = QtWidgets.QGridLayout()

        self.scene = QtWidgets.QGraphicsScene()

        self.view = QtWidgets.QGraphicsView(self.scene, parent=parent)
        layout.addWidget(self.view, 0, 0, 0, 0)
        self.setLayout(layout)

    def add_function_item(self):
        item = RectangleItem()
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.scene.addItem(item)


class RectangleItem(QtWidgets.QGraphicsItem):
    def __init__(self, parent=None):
        super(RectangleItem, self).__init__(parent)
        self.penWidth = 6.0
        self.x_width = 200
        self.y_width = 100
        ButtonItem(self, x_width=self.x_width)

    def boundingRect(self):
        return QtCore.QRectF(-30 - self.penWidth / 2, -30 - self.penWidth / 2,
                      self.x_width + self.penWidth + 30, self.y_width + self.penWidth + 30)

    def _connector_button(self):
        button = QtCore.QRectF(-5, 10, 10, 10)
        return button

    def paint(self, painter, option, widget):
        painter.drawRoundedRect(-10, -10, self.x_width, self.y_width, 5, 5)
        painter.drawText(15, 10, "Function title")


class ButtonItem(QtWidgets.QGraphicsProxyWidget):
    def __init__(self, parent=None, x_width=0):
        super(ButtonItem, self).__init__(parent)
        self.x_width = x_width

        self.pix_map = QtGui.QPixmap()
        # pix_map = self.paintIcon()
        self.paintIcon()
        label = QtWidgets.QLabel()
        label.setPixmap(self.pix_map)
        self.setWidget(label)

        # folder_path = ConfigManager.config_loader()['DEFAULT']['modules_path'] + './protolyse_application_builder'
        # img_pix = QtGui.QPixmap(folder_path + './dist/button_red.gif')
        # img = QtWidgets.QLabel()
        # img.setPixmap(img_pix)
        # self.setWidget(img)

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent):
        print("HOVER")

    def paintIcon(self):
        img = QtGui.QImage()
        painter = QtGui.QPainter(img)
        # painter.begin()
        painter.setBrush(QtGui.QColor(227, 6, 19))
        painter.setPen(QtGui.QColor(34, 43, 63))
        painter.drawRoundedRect(0, 0, 10, 10, 5, 5)
        painter.end()
        self.pix_map.fromImage(img)

'''
    def paint(self, painter, option, widget):
        painter.setBrush(QtGui.QColor(227, 6, 19))
        painter.setPen(QtGui.QColor(34, 43, 63))
        painter.drawRoundedRect(-15, 20, 10, 10, 5, 5)
'''

