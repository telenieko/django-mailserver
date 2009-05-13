DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ':memory:'
INSTALLED_APPS = ['mailserver', 'mailserver.testapp']
ROOT_URLCONF = 'mailserver.urls'
ROOT_MAILCONF = 'mailserver.testapp.mailbox'
DEBUG_PROPAGATE_EXCEPTIONS = True
