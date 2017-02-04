# -*- encoding: utf-8 -*-

import sublime
import sublime_plugin
import os.path
from .functions import *
from .image_manager import ImageManager, ImageManagerError, clear_cache

class settings:
    CURRENT_CHANGE_COUNT = 'markdown_inline_image_current_change_count'

class MarkdownInlineImagesCommand(sublime_plugin.TextCommand):

    def open_url(self, url):
        sublime.run_command('open_url', {'url': url})

    def render_image(self, image_url, base64):
        v = self.view
        if isinstance(base64, Exception):
            msg = "Cannot load '{}': {}".format(image_url, base64)
            # CSW: ignore
            print('MarkdownInlineImages:', msg)
            return sublime.status_message(msg)
        html = '<style>{}</style>'.format(sublime.load_resource('Packages/MarkdownInlineImages/'
                                                                'default.css'))
        html += '<a href="{}"><img src="{}"></a>'.format(image_url, base64)
        display_above = get_settings().get('display_image_above_markup')
        for url, regions in self.images.items():
            if url != image_url:
                continue
            if display_above:
                regions = [sublime.Region(v.line(region.begin()).begin() - 1) for region in regions]
            phantoms = [] + self.phantom_set.phantoms
            for region in regions:
                phantoms.append(sublime.Phantom(region, html, sublime.LAYOUT_BLOCK, self.open_url))
        self.phantom_set.update(phantoms)

    def render_action(self):
        v = self.view
        self.phantom_set = sublime.PhantomSet(v, 'MarkdownInlineImages')
        self.images = {}

        for region in v.find_by_selector('markup.underline.link.image.markdown'):
            url = v.substr(region)
            if not url.startswith(('https://', 'http://')):
                url = os.path.join(os.path.dirname(v.file_name()), url)
            self.images.setdefault(url, []).append(region)

        links_definitions = get_link_definitions(v)
        references = v.find_by_selector('constant.other.reference.link.markdown')
        descriptions = v.find_by_selector('string.other.link.description.markdown')
        for region in v.find_by_selector('meta.image.reference.markdown'):
            ref = get_ref(v, region, references, descriptions)
            self.images.setdefault(links_definitions[ref], []).append(region)

        for url in self.images.keys():
            try:
                ImageManager.get(url, self.render_image)
            except ImageManagerError as e:
                sublime.error_message(str(e))


    def clear_action(self):
        """Remove the images"""
        self.phantom_set.update([])

    def toggle_action(self):
        """Updates the images, but, if it is re-called without any modification being made to the
        buffer, then it hide them"""
        v = self.view
        vsettings = v.settings()
        change_count = vsettings.get(settings.CURRENT_CHANGE_COUNT)
        if change_count == v.change_count():
            self.run(None, 'clear')
            vsettings.erase(settings.CURRENT_CHANGE_COUNT)
        else:
            self.run(None, 'render')
            v.settings().set(settings.CURRENT_CHANGE_COUNT, v.change_count())


    def clear_cache_action(self):
        clear_cache()

    def run(self, edit, action, *args, **kwargs):
        """Run 'action' with the given arguments"""
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
