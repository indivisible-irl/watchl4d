from django.conf import settings
from watchl4d.session import Session
from watchl4d.util import signups_open

def conf(request):
    return {'DEV': settings.DEV,
            'BACKBONE_TEMPLATE_URL': settings.BACKBONE_TEMPLATE_URL,
            'ROOT_URL': settings.ROOT_URL,
            'STATIC_URL': settings.STATIC_URL}

def session(request):
    return {'session': Session(request)}

def signups_open(request):
    return {'signups_open': signups_open()}

