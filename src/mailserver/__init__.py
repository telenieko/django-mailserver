from message import *

import resolvers
import handlers

  
def get_mdaemon():
    from django.conf import settings
    mdaemon = None
    try:
        mdaemon = settings.MAILER_DAEMON_ADDRESS
    except AttributeError:
        return mdaemon or 'daemon@example.com'
