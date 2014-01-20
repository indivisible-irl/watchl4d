"""
WSGI config for watchl4d project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "watchl4d.settings")

curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, curdir + '/../')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
