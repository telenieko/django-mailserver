from django.core.management.base import BaseCommand, CommandError 
from optparse import make_option 
import os 
import sys 
from mailserver.message import EmailRequest
from mailserver.handlers import BaseMessageHandler
from mailserver.exceptions import *
from django.utils import translation

class Command(BaseCommand):
    help = 'Reads an e-mail from STDIN for handling.'
    args = '[optional file name]'

    def handle(self, filename=None, *args, **options):
        if args:
            raise CommandErrors('Usage is runmailserver %s' % self.args)
        if filename:
            f = open(filename, 'r')
        else:
            f = sys.stdin
        message = EmailRequest.from_message_data(f.read())
        handler = BaseMessageHandler()
        try:
            handler(os.environ, message)
        except DeliveryError, e:
            print e.message
            sys.exit(e.status_code)

