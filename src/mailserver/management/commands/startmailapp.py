import os
from django.core.management.commands import startapp

class Command(startapp.Command):
    help = "Creates a Django mail app directory structure for the given app name in the current directory."

    def handle_label(self, app_name, directory=None, **options):
        if directory is None:
            directory = os.getcwd()
        # call startapp...
        super(Command, self).handle_label(app_name, directory, **options)
        top_dir = os.path.join(directory, app_name)
        mboxfile = os.path.join(top_dir, 'mailboxes.py')
        open(mboxfile, 'w').write("""from mailserver.mailbox import *

urlpatterns = patterns('',
  #(r'recipient', '%s.mailers.reply'),
) 
""" % (app_name))

