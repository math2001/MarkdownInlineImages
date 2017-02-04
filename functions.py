# -*- encoding: utf-8 -*-
import base64
import sublime

def convert_to_base64(image_content):
    return 'data:image/png;base64,' \
            + ''.join([chr(el) for el in list(base64.standard_b64encode(image_content))])

def get_settings():
    return sublime.load_settings('MarkdownInlineImages.sublime-settings')


def get_link_definitions(view):
    str_defs = '\n'.join([view.substr(region) for region in \
                         view.find_by_selector('meta.link.reference.def.markdown')])
    defs = {}
    for line in str_defs.splitlines():
        ref, url = line.split(':', 1)
        # removes the spaces and the brackets
        defs[ref.strip()[1:-1]] = url.strip()

    return defs

def get_ref(view, region, references, descriptions):
    references = view.find_by_selector('constant.other.reference.link.markdown')
    descriptions = view.find_by_selector('string.other.link.description.markdown')
    for ref in references:
        if not region.contains(ref):
            continue
        return view.substr(ref) # use the ref
    for description in descriptions:
        if not region.contains(description):
            continue
        return view.substr(description) # use the alt
    raise ValueError("Hasn't found any reference or tag in {}".format(view.file_name() \
                                                                      or view.name()))
