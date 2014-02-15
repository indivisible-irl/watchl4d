import os
import copy
import datetime
import json
import re

from django.conf import settings
from django.shortcuts import render

def generate_backbone_templates(request, src, dest):
    '''
    This does not traverse into sub-directories under src_dir.
    
    :param src: directory containing backbone templates (html files)
    :type src: string
    :param dest: path to destination file to create
    :type dest: string
    
    '''
    if not settings.DEV and os.path.exists(dest):

        # Don't generate if in production and templates are already rendered
        return

    js = ['window.JST = window.JST || {};']
    for filename in os.listdir(src):
        if filename.endswith('.html'):
            template_name = filename[:-5]
            template_text = render(request, filename).content.replace('\n','').replace('"', '\\\"').replace("'", "\\\'")

            js.append("window.JST['{0}'] = _.template('{1}');".format(template_name, template_text))
    
    with open(dest, 'w+') as f:
        f.write('\n'.join(js))

class Object(object):
    def __init__(self, dct):
        for k, v in dct.iteritems():
            self.__dict__[k] = v
            
class RequestObject(Object):
    def __init__(self, request):

        dct = copy.copy(request.GET)
        dct.update(request.POST)
        dct.update(request.FILES)
        super(RequestObject, self).__init__(dct)

    def parse(self, dct):
        parsed_dct = {}
        for k, v in dct.iteritems():
            try:
                parsed_dct[k] = json.loads(v)
            except:
                parsed_dct[k] = v
        return parsed_dct

def signups_open():
    ''' Tournament starts Feb 3, 2014 '''
    return datetime.datetime.now() < datetime.datetime(2014, 2, 3)

def assert_required(val, desc):
    return '' if val.strip() else '{0} is required.<br />'.format(desc)

def assert_min_length(val, length, desc):
    return '' if len(val) >= length else \
        '{0} must be at least {1} characters.<br />'.format(desc, length)

def assert_syntax_steam_id(val, desc):
    matched = re.match('^STEAM_[0-9]:[0-9]:[0-9]+$', val)
    return '' if matched else '{0} is invalid.<br />'.format(desc)

def assert_equal(val1, desc1, val2, desc2):
    return '' if val1 == val2 else \
        '{0} and {1} must match. <br/>'.format(desc1, desc2)

def assert_required_min_length(val, length, desc):
    msg = assert_required(val, desc)
    return msg if msg else assert_min_length(val, length, desc)

def assert_required_syntax_steam_id(val, desc):
    msg = assert_required(val, desc)
    return msg if msg else assert_syntax_steam_id(val, desc)
