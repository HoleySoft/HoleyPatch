# -*- coding: utf-8 -*-
import pysential
from pysential_test import (ScreenRecorder, TestModule, TestWindow)
from electrophys_module import (ePhysModule)


__title__ = "PySential"
__author__ = "Protolyse"
__copyright__ = "Copyright 2020, Protolyse (TM)"
__credits__ = ["Florian L. R. Lucas"]
__license__ = "GPL"
__version__ = "0.0.1.0"
__maintainer__ = "Protolyse (TM)"
__email__ = "info@protolyse.com"
__status__ = "Prototype"


def main() -> None:
    app = pysential.application()

    # app.add_image_path('./img')
    # app.add_image_path('./pysential_images')
    app.load_image_package('./PySential_icos.zip')
    app.load_image_package('./pysential_images.zip')

    app.add_splash(img='splash_loading.png', text="")
    app.set_main_window(title="PySential", img='logo.png')
    app.set_bg(img='bg.png')

    app.add_module(ScreenRecorder)
    app.add_module(TestModule)
    app.add_module(ePhysModule)

    app.run()


if __name__ == '__main__':
    main()
