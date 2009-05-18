from mailserver import EmailResponse
from mailserver import get_setting
from mailserver.context import RequestContext
from mailserver.exceptions import RecipientNotFound
from django.template import loader
from django.utils.safestring import mark_safe

def page_not_found(request, template_name='recipient_notfound.txt', subject=None):
    t = loader.get_template(template_name)
    plain_body = t.render(
        RequestContext(request,
            {'recipient': mark_safe(request.get_recipient_display())}
        ))
    raise RecipientNotFound(plain_body)

def server_error(request):
    pass
