from .base import *
DEBUG = False
ADMINS = (
    ('patrick', 'officexchangesg@gmail.com'),
)
ALLOWED_HOSTS = ['educaproject.com', 'www.educaproject.com']
DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': 'educa',
       'USER': 'educa',
       'PASSWORD': 'Yu20120909$',
   }
}

