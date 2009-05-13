from mailserver.mailbox import *
import sys
import types

testapp = types.ModuleType('testapp2')
testappboxes = types.ModuleType('mailbox')
testapp.mailbox = testappboxes
sys.modules.setdefault('testapp2', testapp)
sys.modules.setdefault('testapp2.mailbox', testappboxes)

testpatterns = patterns('',
  (r'^onedest', 'testapp.mailers.reply'),
  (r'(?P<sender>.+)@(?P<domain>.*)', 'testapp.mailers.echo'),
  (r'(?P<sender>.+)', 'testapp.mailers.echo'),
  )
testappboxes.urlpatterns = testpatterns

urlpatterns = patterns('',
  (r'(\.?)example.net', include('testapp2.mailbox')),
  (r'@bugs.example.com', include('testapp2.mailbox')),
)

def echo(request, sender, domain=None):
    print 'received sender=%s domain=%s' % (sender, domain)
    resp = EmailResponseServer(from_email=request.get_recipient_display(),
        to=request['From'], body=sender,
        subject="Echo Echo")
    resp.sender = sender
    resp.domain = domain
    return resp
