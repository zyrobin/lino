## Copyright 2009-2011 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

"""
This defines Lino default settings. You include this (directly or indirectly) 
into your local :xfile:`settings.py` using::

  from lino.demos.std.settings import *

"""

import os
import sys
from tempfile import gettempdir
from os.path import join, abspath, dirname, normpath
import lino

from lino import LinoSite
LINO_SITE = LinoSite()

#~ DBLOGGER = 'db'
DBLOGFILE = 'auto'
USE_FIREBUG = False
USE_GRIDFILTERS = True
MODEL_DEBUG = True
PROJECT_DIR = normpath(dirname(__file__))
#~ LINO_SETTINGS = join(PROJECT_DIR,"lino_settings.py")
#~ BYPASS_PERMS = True 
BYPASS_PERMS = False
USER_INTERFACES = [
  #~ 'lino.ui.extjsu',
  'lino.ui.extjs'
  ]
DATA_DIR = join(PROJECT_DIR,"data")

#~ BABEL_LANGS = []

APPY_PARAMS = dict(ooPort=8100)
try:
    import uno
except ImportError:
    APPY_PARAMS.update(pythonWithUnoPath=r'C:\PROGRA~1\LIBREO~1\program\python.exe')
    #~ APPY_PARAMS.update(pythonWithUnoPath=r'C:\PROGRA~1\OPENOF~1.ORG\program\python.exe')
    #~ APPY_PARAMS.update(pythonWithUnoPath='/usr/bin/libreoffice')
    #~ APPY_PARAMS.update(pythonWithUnoPath='/etc/openoffice.org3/program/python')


def TIM2LINO_LOCAL(alias,obj):
    """Hook for local special treatment on instances that have been imported from TIM.
    """
    return obj
    
def TIM2LINO_USERNAME(userid):
    if userid == "WRITE": return None
    return userid.lower()
    
    
def TIM2LINO_IS_IMPORTED_PARTNER(obj):
    "`obj` is either a Person or a Company"
    #~ return obj.id is not None and (obj.id < 200000 or obj.id > 299999)
    return False
    #~ return obj.id is not None and (obj.id > 10 and obj.id < 21)
              
    

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG
#TEMPLATE_STRING_IF_INVALID = 'foo'


ADMINS = (
    ('Luc Saffre', 'luc.saffre@gmx.net'),
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(DATA_DIR,'demo.db')
        #~ 'NAME': ':memory:'
    }
}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Brussels'
# TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#~ LANGUAGE_CODE = 'de-BE'
#~ LANGUAGE_CODE = 'fr-BE'

SITE_ID = 1 # see also fill.py

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
# Used by FileSystemStorage.
# Lino generates the :xfile:`site.js` there.
if sys.platform == 'win32': # development server
    MEDIA_ROOT = abspath(join(PROJECT_DIR,'media'))
else:
    MEDIA_ROOT = abspath(join(DATA_DIR,'media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'cqt^18t(Fb#14a@s%mbtdif+ih8fscpf8l9aw+0ivo2!3c(c%&'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

"""
Django and standard HTTP authentication.
http://stackoverflow.com/questions/152248/can-i-use-http-basic-authentication-with-django
"""

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    #'lino.utils.editing.EditingMiddleware',
)


if not BYPASS_PERMS:
    MIDDLEWARE_CLASSES += (
      'django.contrib.auth.middleware.RemoteUserMiddleware',
    )
    AUTHENTICATION_BACKENDS = (
      'django.contrib.auth.backends.RemoteUserBackend',
    )
    
if False:
    MIDDLEWARE_CLASSES += (
      #~ 'lino.utils.sqllog.ShortSQLLogToConsoleMiddleware',
      'lino.utils.sqllog.SQLLogMiddleware',
    )
    

ROOT_URLCONF = 'lino.demos.std.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
      join(abspath(DATA_DIR),'templates'),
      join(abspath(PROJECT_DIR),'templates'),
      join(abspath(dirname(lino.__file__)),'templates'),
)
#print "baz", __file__

INSTALLED_APPS = [
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.sites',
  #~ 'django.contrib.markup',
  #~ 'django.contrib.databrowse',
  
  'lino',
  #~ 'lino.modlib.countries',
  #~ 'lino.modlib.contacts',
  #~ 'lino.modlib.products',
  #~ 'lino.modlib.projects',
  #~ 'lino.modlib.notes',
  
  #~ 'lino.modlib.journals',
  #~ 'lino.modlib.sales',
  #~ 'lino.modlib.ledger',
  #~ 'lino.modlib.finan',
  
  #~ 'lino.modlib.properties',
  #~ 'lino.modlib.links',
  #~ 'lino.modlib.dsbe',
  #~ 'lino.modlib.igen',
  #~ 'south', # http://south.aeracode.org
]


#~ INSTALLED_APPS = []



SERIALIZATION_MODULES = {
     #~ "data" : "lino.utils.dataserializer",
     "dpy" : "lino.utils.dpy",
}

#print "done", __file__

TEMPLATE_CONTEXT_PROCESSORS = (
  "django.core.context_processors.auth",
)

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = "/"

EMAIL_HOST = "mail.example.com"
#EMAIL_PORT = ""

LOGGING_CONFIG = 'lino.utils.log.configure'
LOGGING = dict(filename=None,level='INFO')


gettext = lambda s: s

def language_choices(*args):
    """
    See :doc:`/blog/2011/0226`.
    A subset of Django's LANGUAGES.
    """
    _langs = (
        ('en', gettext('English')),
        ('de', gettext('German')),
        ('fr', gettext('French')),
        ('nl', gettext('Dutch')),
        ('et', gettext('Estonian')),
    )
    return [x for x in _langs if x[0] in args]
      
LANGUAGES = language_choices('en','de','fr','nl','et')
