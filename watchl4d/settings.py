"""
Django settings for watchl4d project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import hashlib
import datetime
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = BASE_DIR + '/watchl4d'
WEBSITE_DIR = PROJECT_DIR + '/website'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^8p&)=iut1(0#e3pa5v*p+qb=o$#0a_gxms4sv5+195d+4&smt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DEV = True

if DEV:
    SERVER_URL = 'http://localhost/'
    ROOT_URL = '/watchl4d/'
    STATIC_URL = '{0}static/'.format(ROOT_URL)
else:
    SERVER_URL = 'http://www.watchl4d.com/'
    ROOT_URL = '/'
    STATIC_URL = '/static/' #TODO

STATIC_VERSION = os.environ.get(
    'WATCHL4D_STATIC_VERSION', 
    hashlib.md5(str(datetime.datetime.now())).hexdigest())

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []

TEMPLATE_DIRS = (WEBSITE_DIR + '/templates',)

BACKBONE_TEMPLATE_FILE = '{0}/static/js/templates.js'.format(WEBSITE_DIR)
BACKBONE_TEMPLATE_URL = '/watchl4d/static/js/templates.js'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'watchl4d.context_processors.conf',
    'watchl4d.context_processors.session',
    'watchl4d.context_processors.signups_open',
    'watchl4d.context_processors.channel_names'
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    'watchl4d.website'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'watchl4d.urls'

WSGI_APPLICATION = 'watchl4d.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'watchl4d',
        'USER': 'website',
        'PASSWORD': 'erparnal',
        'HOST': 'localhost',
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211'
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'mongo': {
            'level': 'INFO',
            'class': 'watchl4d.log.MongoHandler',
            'db': 'watchl4d',
            'collection': 'log'
        }
    },
    'loggers': {
        # no module is specified so that it picks up any module 
        # log name under the base blacklisted folder
        '': { 
            'handlers': ['mongo'],
            'level': 'INFO',
            'propogate': True
        }
    }
}




