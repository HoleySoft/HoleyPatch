# importing the required packages
import pyautogui
import cv2
import copy
import pysential
from pysential.protomodules import (AbstractModule, AbstractThread)
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
        self.ico = "logo"

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

        self.widgets.toolbar_add(self.toolbar, self.face_recognition, img='camera')
        self.widgets.toolbar_add(self.toolbar, self.live_feed, img='view')
        self.widgets.toolbar_add(self.toolbar, self.start_record,
                                 arguments="Recording4.avi", img='record')
        self.widgets.toolbar_add(self.toolbar, self.stop_recording, arguments=None, img='stop')

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
