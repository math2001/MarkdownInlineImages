# -*- encoding: utf-8 -*-

import tempfile
import os
import urllib.request
from threading import Thread
try:
    from .functions import *
except SystemError as e:
    from functions import *

__all__ = ["clear_cache", "ImageManagerError", "ImageLoader", "ImageManager"]

TIMEOUT = 20 # seconds

CACHE_FILE = os.path.join(tempfile.gettempdir(), 'SublimeTextMarkdownInlineImages.cache.txt')

CACHE_LINE_SEPARATOR = '-%-CACHE-SEPARATOR-%-'

def clear_cache():
    os.remove(CACHE_FILE)

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
    def get_cache_for(cls, url):
        if not os.path.exists(CACHE_FILE):
            return
        with open(CACHE_FILE) as fp:
            for line in fp:
                line = line.split(CACHE_LINE_SEPARATOR, 1)
                if line[0] == url:
                    return line[1]

    @classmethod
    def get_callback_for(cls, url, user_callback):
        def callback(image_content):
            del cls.currently_loading_images[url]
            if isinstance(image_content, Exception):
                return user_callback(url, image_content)
            base64 = convert_to_base64(image_content)
            with open(CACHE_FILE, 'a') as fp:
                fp.write('\n' + url + CACHE_LINE_SEPARATOR + base64)
            user_callback(url, base64)
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
            return user_callback(url, cache)

        # actually load the image
        # _callback will save the image to the cache AND run the user callback with the base64 image
        callback = cls.get_callback_for(url, user_callback)
        cls.currently_loading_images[url] = ImageLoader(url, callback)
        cls.currently_loading_images[url].start()

if __name__ == '__main__':
    callback = lambda path, base64: print("Got '{}', '{}'".format(path, base64[:50]))

    ImageManager.get('https://i.ytimg.com/vi/C2O7lM0bU0g/maxresdefault.jpg', callback)
    ImageManager.get("http://2017.animationdingle.com/wp-content/uploads/2016/08/hello_world.gif", callback)
