from message import *
import exceptions
import resolvers
import handlers

DEFAULT_SETTINGS = {
    'MAIL_DAEMON_ADDRESS': 'daemon@example.com',
    'ROOT_MAILCONF': 'mailbox',
    'MAIL_TEMPLATE_CONTEXT_PROCESSORS': (
        'mailserver.context.request',
        'mailserver.context.media',
        'mailserver.context.i18n',
        ),
    'MAIL_MIDDLEWARE': (
        'django.middleware.transaction.TransactionMiddleware',

    ),
}
  
def get_setting(setting):
    from django.conf import settings
    default = DEFAULT_SETTINGS[setting]
    return getattr(settings, setting, default)
