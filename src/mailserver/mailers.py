from mailserver import EmailResponse, EmailResponseNotFound
from mailserver import get_setting
from mailserver.context import RequestContext
from django.template import loader
from django.utils.safestring import mark_safe

def page_not_found(request, template_name='recipient_notfound.txt', subject=None):
    if subject is None:
        subject="Mail delivery failed: returning message to sender"
    t = loader.get_template(template_name)
    plain_body = t.render(
        RequestContext(request,
            {'recipient': mark_safe(request.get_recipient_display())}
        ))
    response = EmailResponseNotFound(
        from_email=get_setting('MAIL_DAEMON_ADDRESS'),
        to=request['From'],
        body=plain_body, subject=subject)
    return response

def server_error(request):
    pass
