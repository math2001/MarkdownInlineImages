# -*- encoding: utf-8 -*-

import sublime
import sublime_plugin
import os.path
from .image_manager import ImageManager, ImageManagerError, clear_cache

class MarkdownInlineImagesCommand(sublime_plugin.TextCommand):

    def open_url(self, url):
        sublime.run_command('open_url', {'url': url})

    def render_image(self, image_url, base64):
        if isinstance(base64, Exception):
            msg = "Cannot load '{}': {}".format(image_url, base64)
            # CSW: ignore
            print(msg)
            return sublime.status_message(msg)
        html = '<style>{}</style>'.format(sublime.load_resource('Packages/MarkdownInlineImages/'
                                                                'default.css'))
        html += '<a href="{}"><img src="{}"></a>'.format(image_url, base64)
        for url, region in self.images.items():
            if url != image_url:
                continue
            ph = self.phantom_set.phantoms + [sublime.Phantom(region, html, sublime.LAYOUT_BLOCK,
                                                 self.open_url)]
        self.phantom_set.update(ph)

    def render_action(self):
        v = self.view
        self.phantom_set = sublime.PhantomSet(v, 'MarkdownInlineImages')
        self.images = {}

        for region in v.find_by_selector('markup.underline.link.image.markdown'):
            url = v.substr(region)
            if not url.startswith(('https://', 'http://')):
                url = os.path.join(os.path.dirname(v.file_name()), url)
            self.images[url] = region

        for url in self.images.keys():
            try:
                ImageManager.get(url, self.render_image)
            except ImageManagerError as e:
                sublime.error_message(str(e))

    def clear_cache_action(self):
        clear_cache()

    def run(self, edit, action, *args, **kwargs):
        try:
            func = getattr(self, action.replace(' ', '_') + '_action')
        except AttributeError:
            sublime.error_message("MarkdownInlineImages: Trying to run a non-existing command: "
                                  "'{}'".format(action))
        else:
            func(*args, **kwargs)

    def is_enabled(self, action):
        return action == 'render' and 'markdown' in self.view.scope_name(-1).lower() \
               or action != 'render'
