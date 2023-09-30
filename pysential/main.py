# -*- coding: utf-8 -*-
import pysential
# from pysential_test import (ScreenRecorder, TestModule, TestWindow)
from electrophys_module import (ePhysModule, ePhysModule_SingleChannel)

# from template_module import TestModule


__title__ = "PySential - HoleyPatch"
__author__ = "Florian L. R. Lucas"
__copyright__ = "Copyright 2023"
__credits__ = ["Florian L. R. Lucas", "Carsten Wloka"]
__license__ = "BSD-3"
__version__ = "1.0"
__maintainer__ = "Florian L. R. Lucas"
__status__ = "Prototype"


def main() -> None:
    app = pysential.application()

    app.load_image_package('./PySential_icos.zip')
    app.load_image_package('./pysential_images.zip')

    app.add_splash(img='splash_loading.png', text="")
    app.set_main_window(title="HoleyPatch", img='logo.png')
    app.set_bg(img='bg.png')

    app.add_module(ePhysModule)
    # app.add_module(TestModule)
    app.run()

if __name__ == '__main__':
    main()
