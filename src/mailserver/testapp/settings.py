import os
PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ':memory:'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'mailserver', 'mailserver.testapp']
ROOT_URLCONF = 'mailserver.urls'
ROOT_MAILCONF = 'mailserver.testapp.mailbox'
DEBUG_PROPAGATE_EXCEPTIONS = True
TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'), 
    )
