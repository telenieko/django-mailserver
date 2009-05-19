# -*- coding: UTF-8 -*-
from django.http import Http404
from django.template import loader
from django.utils.safestring import mark_safe
from mailserver.context import RequestContext
from mailserver import EmailResponse
from mailserver import get_setting

class DeliveryError(Exception):
    # Persistent Transeint Failures start with '4'
    status_code = 400
    template_name = None # Template to use in get_response
    subject = None

    def get_context(self, request):
        return {'recipient': mark_safe(request.get_recipient_display()),
            'message': self.message}

    def get_response(self, request):
        # Helper method to provide nice responses for errors.
        # 'cause you know people do not read Mailer Delivery errors...
        from_email = get_setting('MAIL_DAEMON_ADDRESS')
        context = self.get_context(request)
        if self.template_name is None:
            body = "Temporary delivery failure"
        else:
            t = loader.get_template(self.template_name)
            body = t.render(RequestContext(request, context))
        subject = self.subject
        if subject is None:
            subject = "Mail delivery problem"
        response = EmailResponse(from_email=from_email, to=request['From'],
            body=body, subject=subject)
        response.status_code = self.status_code
        return response


class PermanentDeliveryError(DeliveryError):
    # Permanent Failures start with '5'
    status_code = 500
    template_name = "mailserver_error.txt"
    subject = "Permanent delivery error"

class PermissionDenied(PermanentDeliveryError):
    status_code = 530
    template_name = 'recipient_denied.txt'
    subject = 'Access Denied to Recipient'
    
class RecipientNotFound(PermanentDeliveryError):
    status_code = 511
    template_name = 'recipient_notfound.txt'
    subject = 'Invalid Recipient Address'


#class MailerDoesNotExist(RecipientNotFound):
#    pass

class ContentNotFound(DeliveryError):
    pass


from django.core import exceptions
from django import http
class ExceptionMapperMiddleware(object):
    """ Middleware class that captures a Django standard
        Exception, and raises the "Mail" equivalent.
        i.e: Http404 > RecipientNotFound
    """
    def process_exception(self, request, e):
        if issubclass(e.__class__, http.Http404):
            raise RecipientNotFound(e.message)
