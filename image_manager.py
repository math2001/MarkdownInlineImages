# -*- encoding: utf-8 -*-

import tempfile
import os.path
import urllib.request
from threading import Thread
try:
    from .functions import *
except SystemError as e:
    from functions import *

TIMEOUT = 20 # seconds

CACHE_FILE = os.path.join(tempfile.gettempdir(), 'SublimeTextMarkdownInlineImages.cache.txt')

class ImageManagerError(Exception):
    pass

class ImageLoader(Thread):

    def __init__(self, url, callback):
        Thread.__init__(self)
        self.url = url
        self.callback = callback

    def run(self):
        if not self.url.startswith(('http://', 'https://')):
            with open(self.url, 'rb') as fp:
                self.callback(fp.read())
            return
        try:
            page = urllib.request.urlopen(self.url, None, TIMEOUT)
        except Exception as e:
            self.callback(e)
        else:
            self.callback(page.read())

class ImageManager:

    """Loads a local or remote image, converts it to base64, saves it to a cache fiel and run the
    user callback"""

    currently_loading_images = {}

    @classmethod
    def get_cache_for(cls, path):
        if not os.path.exists(CACHE_FILE):
            return
        with open(CACHE_FILE) as fp:
            for line in fp:
                line = line.split(CACHE_LINE_SEPARATOR, 1)
                if line[0] == path:
                    return line[1]

    @classmethod
    def get_callback_for(cls, path, user_callback):
        def callback(image_content):
            base64 = convert_to_base64(image_content)

            user_callback(path, base64)
        return callback

    @classmethod
    def get(cls, url, user_callback):
        """url can be a local path too
        user_callback is a function that takes the path, and the base64 content
        """

        if url in cls.currently_loading_images:
            raise ImageManagerError("Currently loading the image '{}'".format(url))

        cache = cls.get_cache_for(url)
        if cache:
            user_callback(cache)

        # actually load the image
        # _callback will save the image to the cache AND run the user callback with the base64 image
        callback = cls.get_callback_for(url, user_callback)
        cls.currently_loading_images[url] = ImageLoader(url, callback)
        cls.currently_loading_images[url].start()

ImageManager.get("C:\\Users\\Home\\Pictures\\__bg\\penrose-triangle.jpg",
                 lambda path, base64: print("Got '{}', '{}'".format(path, base64[:50])))
