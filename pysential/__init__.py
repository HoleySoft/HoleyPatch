# -*- coding: utf-8 -*-
from . import gui
from .default_modules import (pyside2_gui)
from .package_manager import ImageManager

import logging
logger = logging.getLogger(__name__)

__version__ = "0.0.1"


def application() -> object:
    app = MainApplication()
    app.set_gui(pyside2_gui)
    return app


class MainApplication:
    def __init__(self) -> None:
        self.gui_module = None
        self.modules = list()
        self.splash = None
        self.main_window = None
        self.bg_img = None
        self.textures = None
        self.image_manager = ImageManager()

    def add_image_path(self, path):
        self.image_manager.add_root(path)

    def load_image_package(self, filename):
        self.image_manager.load_package(filename)

    def set_bg(self, img=''):
        self.bg_img = self.image_manager.get_image(img)

    def set_main_window(self, title=None, img=None):
        img = self.image_manager.get_image(img)
        self.main_window = (title, img)

    def add_splash(self, img=None, text=None):
        img = self.image_manager.get_image(img)
        self.splash = (img, text)

    def add_module(self, module, *args, **kwargs):
        self.modules.append(module)

    def set_gui(self, obj: object) -> None:
        self.gui_module = obj

    def run(self) -> None:
        try:
            self.gui_module.run(self)
        except AttributeError as e:
            logger.error(e, exc_info=True)
