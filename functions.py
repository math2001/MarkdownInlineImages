# -*- encoding: utf-8 -*-
import base64
import sublime

def convert_to_base64(image_content):
    return 'data:image/png;base64,' \
            + ''.join([chr(el) for el in list(base64.standard_b64encode(image_content))])

def get_settings():
    return sublime.load_settings('MarkdownInlineImages.sublime-settings')
