# importing the required packages
import pyautogui
import cv2
import copy
import pysential
from pysential.protomodules import (AbstractModule, AbstractThread, AbstractWindow)
import numpy as np
import time
import PIL.ImageGrab


def live_feed(feed):
    a = time.time()
    img = pyautogui.screenshot()
    # img = PIL.ImageGrab.grab()
    frame = np.array(img)
    feed.frame = frame
    feed.fps = 1 / (time.time()-a)


def render_feed(feed):
    feed.set_feed()


class FeedClass:
    def __init__(self, media_feed):
        self.media_feed = media_feed
        self.frame = None
        self.fps = None
        self.masks = []

    def set_frame(self, frame):
        self.frame = frame

    def set_masks(self, masks):
        self.masks = masks

    def set_feed(self):
        try:
            frame = copy.deepcopy(self.frame)
            masks = copy.deepcopy(self.masks)
            for (x, y, w, h) in masks:
                frame = cv2.rectangle(frame,
                                      (int(x), int(y)),
                                      (int((x + w)), int((y + h))),
                                      (255, 0, 0), 2
                                      )
            self.media_feed.set_image(frame)
        except ValueError:
            pass


def recognize_face(args):
    feed, face_cascade = args
    frame = copy.deepcopy(feed.frame)
    faces = face_cascade.detectMultiScale(frame, 1.1, 4)
    feed.set_masks(faces)


class ScreenRecorder(AbstractModule):
    def __init__(self, obj: object, fps=24) -> None:
        # Inherent AbstractModule
        super(ScreenRecorder, self).__init__(obj)

        # Set the title of the workspace
        # Set workspace icon
        self.title = "Face recognition"
        self.ico = "./img/logos/logo.png"

        # Show when starting the program
        self.show = True

        self.feed_threads = []
        self.face_recognition_threads = []
        self.face_recognition_active = False
        self.fps = fps
        self.record, self.media_feed, self.toolbar = False, None, None
        self.codec = cv2.VideoWriter_fourcc(*"XVID")
        self.feed = None
        self.feed_fps = 0
        self.feed_time = 0

    def run(self, win: object):
        # Setup a new window
        self.new_window(win)

        self.toolbar = self.widgets.make_toolbar(grid=(0, 20, 0, 1))

        self.widgets.toolbar_add(self.toolbar, self.face_recognition, img='./img/icons/camera.gif')
        self.widgets.toolbar_add(self.toolbar, self.live_feed, img='./img/icons/view.gif')
        self.widgets.toolbar_add(self.toolbar, self.start_record,
                                 arguments="Recording4.avi", img='./img/icons/record.gif')
        self.widgets.toolbar_add(self.toolbar, self.stop_recording, arguments=None, img='./img/icons/stop.gif')

        self.media_feed = self.widgets.media_feed(grid=(0, 20, 1, 10))

        # Set window contents (finish)
        self.set_content()

    @ staticmethod
    def screenshot(self):
        img = pyautogui.screenshot()

    def face_recognition(self):
        if self.face_recognition_active:
            for i in self.face_recognition_threads:
                i.stop()
                i.join()
            self.face_recognition_threads = []
            self.feed.set_masks([])
            self.face_recognition_active = False
        else:
            if not self.feed:
                self.live_feed()
            face_cascade = cv2.CascadeClassifier()
            face_cascade.load('data/haarcascades/haarcascade_frontalface_default.xml')
            self.face_recognition_threads.append(
                AbstractThread(self, func=recognize_face,
                               arguments=(self.feed, face_cascade),
                               recurrent=True)
            )
            for i in self.face_recognition_threads:
                i.start()
            self.face_recognition_active = True

    def live_feed(self):
        self.feed = FeedClass(self.media_feed)
        self.feed_threads.append(
            AbstractThread(self, func=live_feed,
                           arguments=self.feed,
                           recurrent=True)
        )

        self.feed_threads.append(
            AbstractThread(self, func=render_feed,
                           arguments=self.feed,
                           recurrent=True)
        )

        for i in self.feed_threads:
            i.start()

    def start_record(self, filename, resolution=(1920, 1080)):
        self.record = True
        out = cv2.VideoWriter(filename, self.codec, self.fps, resolution)
        while self.record:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
        out.release()

    def stop_recording(self):
        self.record = False
        for i in self.face_recognition_threads:
            i.stop()
            i.join()
        for i in self.feed_threads:
            i.stop()
            i.join()
        self.feed_threads = []


class TestModule(AbstractModule):
    def __init__(self, obj: object) -> None:
        # Inherent AbstractModule
        super(TestModule, self).__init__(obj)

        # Set the title of the workspace
        # Set workspace icon
        self.title = "Workspace title"
        self.ico = "./img/logos/logo.png"

        # Show when starting the program
        self.show = True

        # Add menu bar items
        self.add_menu('Tests', 'Test', self.test_function)
        self.add_menu('Tests', 'Test2', self.test_function)
        self.add_menu('Tests2', 'Test', self.test_function2, args="TETETE")

        self.list_view = None
        self.toolbar = None
        self.chart_view = None
        self.chart_view2 = None
        self.test_window = TestWindow(obj)

    def run(self, win: object):
        # Setup a new window
        self.new_window(win)

        # Data (random)
        x = np.linspace(0, 100, 100)
        y = np.random.rand(100)

        # Content use grid as tuple (x0, x1, y0, y1)
        # self.widgets.make_tree_view(function_connect=self._tree_view_clicked, grid=(0, 5, 2, 12))
        # self.widgets.make_tree_view(function_connect=self._tree_view_clicked, grid=(5, 15, 2, 12))
        self.widgets.multiple_trees(function_connect=self._tree_view_clicked, grid=(0, 5, 2, 12))
        self.widgets.multiple_trees(function_connect=self._tree_view_clicked, grid=(5, 15, 2, 12))
        self.widgets.make_tree_view(function_connect=self._tree_view_clicked, grid=(15, 20, 2, 12))

        # With border
        self.widgets.make_button(function_connect=self.test_window.run, grid=(0, 1, 0, 1),
                                 img='./img/icons/openFolder.gif')
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(1, 2, 0, 1),
                                 text='button')
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(0, 1, 1, 2),
                                 text='button', img='./img/icons/openFolder.gif')
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(1, 2, 1, 2))

        # Without border
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(2, 3, 0, 1),
                                 border=False, img='./img/icons/openFolder.gif')
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(3, 4, 0, 1),
                                 border=False, text='button')
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(2, 3, 1, 2),
                                 border=False, text='button', img='./img/icons/openFolder.gif')
        self.widgets.make_button(function_connect=self._tree_view_clicked, grid=(3, 4, 1, 2), border=False)

        self.toolbar = self.widgets.make_toolbar(grid=(4, 20, 0, 2))

        self.widgets.toolbar_add(self.toolbar, self.test_function, arguments=None, img='./img/icons/openFolder.gif')
        self.widgets.toolbar_add(self.toolbar, self.test_function, arguments=None, img='./img/icons/save.gif')
        self.widgets.toolbar_add(self.toolbar, self.test_function, arguments=None, img='./img/icons/settings.gif')

        # Make a chart
        self.chart_view = self.widgets.make_chart_view(grid=(0, 10, 12, 22))
        self.widgets.add_chart_data(self.chart_view, x_data=x, y_data=y)
        self.widgets.add_chart_data(self.chart_view, x_data=x, y_data=y[::-1])

        self.chart_view2 = self.widgets.make_chart_view(grid=(10, 20, 12, 22))
        self.widgets.add_chart_data(self.chart_view2, x_data=x, y_data=y)

        # Set window contents (finish)
        self.set_content()

    @ staticmethod
    def _tree_view_clicked(file_path):
        print(file_path)

    @ staticmethod
    def test_function():
        print("Test")

    @ staticmethod
    def test_function2(i):
        print(i)


class TestWindow(AbstractWindow):
    def __init__(self, obj: object) -> None:
        # Inherent AbstractModule
        super(TestWindow, self).__init__(obj)

        # Set the title of the workspace
        # Set workspace icon
        self.title = "Face recognition"
        self.ico = "./img/logos/logo.png"
        self.toolbar = None

    def run(self):
        self.toolbar = self.widgets.make_toolbar(grid=(0, 20, 0, 1))

        self.widgets.toolbar_add(self.toolbar, self.test_function, img='./img/icons/camera.gif')
        self.widgets.toolbar_add(self.toolbar, self.test_function, img='./img/icons/view.gif')
        self.widgets.toolbar_add(self.toolbar, self.test_function, img='./img/icons/record.gif')
        self.widgets.toolbar_add(self.toolbar, self.test_function, arguments=None, img='./img/icons/stop.gif')

        self.media_feed = self.widgets.media_feed(grid=(0, 20, 1, 10))

        # Set window contents (finish)
        self.set_content()

    @staticmethod
    def test_function():
        print("Test")


def main() -> None:
    app = pysential.application()
    app.add_splash(img='./img/img/splash_loading.png', text="TEXT")
    app.set_main_window(title="Protolyse", img='./img/logos/logo.png')
    app.set_bg(img='./img/img/bg.png')
    app.add_module(ScreenRecorder)
    app.add_module(TestModule)
    app.run()


if __name__ == '__main__':
    main()
