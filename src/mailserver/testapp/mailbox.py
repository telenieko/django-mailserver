from mailserver.mailbox import *
import sys
import types

testapp = types.ModuleType('testapp2')
testappboxes = types.ModuleType('mailbox')
testapp.mailbox = testappboxes
sys.modules.setdefault('testapp2', testapp)
sys.modules.setdefault('testapp2.mailbox', testappboxes)

testpatterns = patterns('',
  (r'^destination$', 'testapp.mailers.echo'),
  (r'^login$', 'testapp.mailers.login_echo'),
  (r'^except$', 'testapp.mailers.raise_exception'),
  )
testappboxes.urlpatterns = testpatterns

urlpatterns = patterns('',
  (r'@example.com', include('testapp2.mailbox')),
)

