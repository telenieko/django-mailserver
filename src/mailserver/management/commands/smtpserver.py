from django.core.management.base import BaseCommand, CommandError 
from django.db.transaction import commit_on_success
from optparse import make_option 
import smtpd
import asyncore
import os 
import sys 
from mailserver.message import EmailRequest
from mailserver.handlers import BaseMessageHandler
from mailserver.exceptions import DeliveryError
from django.utils import translation

class SMTPServer(smtpd.SMTPServer):
    def __init__(self, *args, **kwargs):
        smtpd.SMTPServer.__init__(self, *args, **kwargs)
        self.handler = BaseMessageHandler()

    def process_message(self, *args, **kwargs):
        try:
            real_process_message(self, *args, **kwargs)
        except DeliveryError, e:
            return u"%s %s" % (e.status_code, e.message)

    def real_process_message(self, peer, mailfrom, rcpttos, data):
        for recipient in rcpttos:
            message = EmailRequest.from_message_data(data, recipient)
            response = self.handler(os.environ, message)

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--listen', '-l', dest='listen', default="localhost",
            help='Address to listen on.'),
        make_option('--port', '-p', dest='port', default=25,
            help='Port to listen on.'),
    )
    help = 'Runs an SMTP server waitting for messages'

    def handle(self, *args, **options):
        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C' 
        listen = options.get('listen')
        port = int(options.get('port'))
        server = SMTPServer((listen, port), None)
        try:
            while 1:
                asyncore.loop(timeout=0.001, count=1)
        except KeyboardInterrupt:
            server.close()
        except:
            server.close()
            raise
            

