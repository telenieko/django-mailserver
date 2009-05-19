from mailserver import EmailResponse
from django.template import loader
from django.utils.safestring import mark_safe
from mailserver.context import RequestContext
from mailserver.auth import login_required

def echo(request, sender=None, domain=None):
    t = loader.get_template('recipient_notfound.txt')
    plain_body = t.render(
        RequestContext(request, {'sender': sender, 'domain': domain})
        )
    resp = EmailResponse(
        from_email=request.get_recipient_display(),
        to=request['From'], body=plain_body,
        subject="Echo Echo")
    return resp

login_echo = login_required(echo)
