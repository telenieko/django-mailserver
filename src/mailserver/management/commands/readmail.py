from django.core.management.base import BaseCommand, CommandError 
from optparse import make_option 
import os 
import sys 
from mailserver.message import EmailRequest
from mailserver.handlers import BaseMessageHandler
from django.utils import translation

class Command(BaseCommand):
    help = 'Reads an e-mail from STDIN for handling.'
    args = '[optional file name]'

    requires_model_validation = False

    def handle(self, filename=None, *args, **options):
        if args:
            raise CommandErrors('Usage is runmailserver %s' % self.args)
        if filename:
            f = open(filename, 'r')
        else:
            f = sys.stdin
        shutdown_message = options.get('shutdown_message', '') 
        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C' 
        message = EmailRequest.from_message_data(f.read())
        handler = BaseMessageHandler()
        res = handler(os.environ, message)
        print res
