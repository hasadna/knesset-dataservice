# encoding: utf-8
# Django settings for knesset-data-django testing app
import os
from knesset_data_django import KNESSET_DATA_DJANGO_APPS

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = "=/30yw[tzR<TYgUtYH9jwq>)xJfWJ#l9ky!^s_ob#1Q8)MUN,p"

DATABASES = {
    'default': {
        'NAME': 'dev.db',
        'ENGINE': 'django.db.backends.sqlite3'
    },
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Jerusalem'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'he'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.path.pardir
))

DATA_ROOT = os.path.join(PROJECT_ROOT, 'data', '')

# these are required by tinymce module
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static', '')

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.comments',
    'django.contrib.sitemaps',
    'django.contrib.flatpages',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tagging',
    'south',
    'planet',
    'django_extensions',
    'actstream',
    'annotatetext',
    'mailer',
    'djangoratings',
    'voting',
    'waffle',
    'django_nose',
    # knesset apps
    'auxiliary',
    'mks',
    'mmm',
    'laws',
    'committees',
    'simple',
    'tagvotes',
    'accounts',
    'links',
    'user',
    'agendas',
    'notify',
    'persons',
    'events',
    'video',
    'okhelptexts',
    'tastypie',
    'polyorg',
    'plenum',
    'tinymce',
    'suggestions',
    'okscraper_django',
    'lobbyists',
    'kikar',
    'ok_tag',
    'dials',
) + KNESSET_DATA_DJANGO_APPS

LONG_CACHE_TIME = 60

TEST_RUNNER = 'knesset_data_django.common.testing.test_runner.KnessetDataDjangoTestRunner'


try:
    from local_settings import *
except ImportError:
    pass
