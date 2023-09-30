# -*- coding: utf-8 -*-
# System default libraries
from functools import partial
import os
import sys
import copy

# Third party libraries
from PySide2 import (QtGui, QtCore)
from PySide2.QtCore import *
from PySide2.QtWidgets import (QMainWindow, QWidget, QMdiSubWindow, QAction, QGridLayout)

# Custom libraries
from .mdi_area import *

import logging
logger = logging.getLogger(__name__)


class Main(QMainWindow):
    """Main class for PySide2 based GUI

    Attributes
    ----------
    menus : list
        List of many items
    widgets : list
        List containing widgets
    work_spaces : list
        List containing work spaces
    obj : object
        Main object, passed to children
    modules : list
        List of available modules
    mdi : MdiArea
        MdiArea widget

    Methods
    ----------
    init_workspace(module, *args, **kwargs)
        Initializes a new work space from module
    closeEvent(event)
        Close all active widgets upon close
    close_ui
        Close Main
    show_ui
        Show Main
    add_menu_items
        Add the menu items read from modules
    dragEnterEvent(e)
        Triggered when items are dragged into main
    dragMoveEvent(e)
        Triggered when items are moved over main
    dropEvent(e)
        Triggered when items are dropped into main
    """
    def __init__(self, obj: object) -> None:
        super(Main, self).__init__()
        self.threads, self.workers = list(), list()
        self.threadpool = QtCore.QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.menus, self.widgets, self.work_spaces = list(), list(), list()
        obj.parent = self
        self.obj = obj
        self.modules = [module(obj) for module in obj.modules]

        self.mdi = MdiArea(img=obj.bg_img)
        self.add_menu_items()

        # Scan over all modules and load those that have the show flag enabled
        [self.init_workspace(module) for module in self.modules if module.show]

        # Allow item drops
        self.setAcceptDrops(True)

    def init_workspace(self, module, *args, **kwargs) -> None:
        """Initializes a new work space from module

        Parameters
        ----------
        module : class
            Module class to be initialized
        """
        self.widgets.append(QWidget())
        self.widgets[-1].is_alive = True
        self.work_spaces.append(QMdiSubWindow())
        self.work_spaces[-1].setWindowTitle(module.title)
        img = self.obj.image_manager.get_image(module.ico)
        self.work_spaces[-1].setWindowIcon(QtGui.QIcon(img))
        self.work_spaces[-1].setWidget(self.widgets[-1])
        self.mdi.addSubWindow(self.work_spaces[-1])
        self.work_spaces[-1].showMaximized()
        self.widgets[-1].layout = QGridLayout()
        '''
        worker = Worker(module.run, self.widgets[-1])
        worker.signals.progress.connect(self.update_content)
        self.threadpool.start(worker)
        '''
        self.threads.append(QtCore.QThread())
        self.workers.append(WidgetsThreads())
        self.workers[-1].moveToThread(self.threads[-1])
        self.threads[-1].started.connect(lambda: self.workers[-1].run(module, self.widgets[-1]))
        # worker.finished.connect(thread.quit)
        self.threads[-1].start()
        # worker.run(module, self.widgets[-1])
        # module.run(self.widgets[-1])


    def update_content(self, *args, **kwargs):
        module = args[0]
        print(module.win)
        print(self.widgets[-1])
        self.mdi.addSubWindow(module.win)
        self.widgets[-1] = module.win


    def closeEvent(self, event):
        """Close all active widgets upon close

        Parameters
        ----------
        event
            Event information
        """
        for widget in self.widgets:
            widget.is_alive = False
        self.close_ui()

    def close_ui(self) -> None:
        """Close Main
        """
        self.close()

    def show_ui(self) -> None:
        """Show Main
        """
        # Set the program content
        self.setCentralWidget(self.mdi)
        self.showMaximized()

        # Set the title and icon
        title, img = self.obj.main_window
        self.setWindowTitle(title)
        if img:
            self.setWindowIcon(QtGui.QIcon(img))
        self.show()

    @ staticmethod
    def _post_function(trigger: str, args=None) -> None:
        if args:
            trigger(args)
        else:
            trigger()

    def add_menu_items(self) -> None:
        """Add the menu items read from modules
        """
        def _add_item(menu, key, trigger, args=None):
            action = QAction('&' + menu, self)
            action.triggered.connect(partial(self._post_function, trigger, args=args))
            self.menus[roots.index(key)].addAction(action)
        try:
            roots = []
            for module in self.modules:
                for item in module.menu_bar:
                    if item[0] not in roots:
                        roots.append(item[0])
            if 'View' not in roots:
                roots.append('View')
            self.menus = [self.menuBar().addMenu('&' + i.capitalize()) for i in roots]

            for module in self.modules:
                if module.title != "":
                    _add_item(module.title, 'View', self.init_workspace, args=module)
                for item in module.menu_bar:
                    if len(item) == 4:
                        _add_item(item[1], item[0], item[2], args=item[3])
                    else:
                        _add_item(item[1], item[0], item[2])
        except AttributeError as e:
            logger.error(e, exc_info=True)

    # The following three methods set up dragging and dropping for the app
    def dragEnterEvent(self, e):
        """Triggered when items are dragged into main

        Parameters
        ----------
        e
            Event information
        """
        if e.mimeData().hasUrls:
            e.accept()

        else:
            e.ignore()

    def dragMoveEvent(self, e):
        """Triggered when items are moved over main

        Parameters
        ----------
        e
            Event information
        """
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """Triggered when items are dropped into main

        Parameters
        ----------
        e
            Event information
        """
        if e.mimeData().hasUrls:
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
            for url in e.mimeData().urls():
                file_path = str(url.toLocalFile())
                for module in self.obj.modules:
                    try:
                        response = module(self.obj).handle_file(file_path)
                        if response:
                            self.init_workspace(response)
                            break
                    except AttributeError:
                        pass
        else:
            e.ignore()


class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress
        self.kwargs['result_callback'] = self.signals.result
        self.kwargs['finished_callback'] = self.signals.finished

    @Slot()  # QtCore.Slot
    def run(self):
        self.fn(*self.args, **self.kwargs)
        self.signals.finished.emit()


class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(object)


class WidgetsThreads(QtCore.QThread):
    def run(self, module, parent):
        module.run(parent)
