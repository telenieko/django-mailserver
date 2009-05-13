from mailserver import resolvers
from mailserver.exceptions import *
from mailserver import EmailResponse, EmailResponseServer
from mailserver import EmailIgnoreResponse
import logging
import sys

class BaseMessageHandler(object):
    def __call__(self, environ, request):
        logging.debug("processing message %s" % request)
        resp = self.get_response(request)
        # Need to handle when the reply is to be sent
        # Or needs to not mark-as-delivered
        if isinstance(resp, EmailResponseServer):
            # Some king of error we have to tell the MTA about.
            # (User gets nothing (from our part))
            return resp
        elif isinstance(resp, EmailIgnoreResponse):
            pass
        elif isinstance(resp, EmailResponse):
            # Some kind of normal response, we send to the user.
            resp.send()
        else:
            raise ValueError, "Do not know how to handle response %s" % resp
        return None
      
    def __repr__(self):
        return self.__class__.__name__

    def get_response(self, request):
        from django.core import exceptions
        from django.conf import settings
        mailconf = getattr(request, "mailconf", settings.ROOT_MAILCONF)
        resolver = resolvers.RegexMailResolver(r'', mailconf)
        try:
            callback, callback_args, callback_kwargs = \
                resolver.resolve(request.get_recipient_address())
            # TODO: Middlewares
            try:
                response = callback(request, *callback_args, **callback_kwargs)
            except Exception, e:
                # TODO: Exception Middleware
                raise
            # Complain if the view returned None (a common error).
            if response is None:
                try:
                    view_name = callback.func_name
                except AttributeError:
                    view_name = callback.__class__.__name__ + '.__call__'
                raise ValueError, "The view %s.%s didn't return a meaningfull response" % (callback.__module__, view_name)
            return response
        except exceptions.PermissionDenied:
            # How should we handle this?
            raise
        except resolvers.Resolver404, e:
            try:
                callback, param_dict = resolver.resolve404()
                return callback(request, **param_dict)
            except:
                return self.handle_uncaught_exception(
                    request, resolver, sys.exc_info())
        except SystemExit:
            raise
        except:
            exc_info = sys.exc_info()
            return self.handle_uncaught_exception(request, resolver, exc_info)
            
    def handle_uncaught_exception(self, request, resolver, exc_info):
        from django.conf import settings
        from django.core.mail import mail_admins

        if settings.DEBUG_PROPAGATE_EXCEPTIONS:
            raise

        # When DEBUG is False, send an error message to the admins.
        subject = 'Mail Error (%s)' % request['From'][1]
        try:
            request_repr = repr(request)
        except:
            request_repr = "Request repr() unavailable"
        message = "%s\n\n%s" % (self._get_traceback(exc_info), request_repr)
        mail_admins(subject, message, fail_silently=True)
        # Return an HttpResponse that displays a friendly error message.
        callback, param_dict = resolver.resolve500()
        return callback(request, **param_dict)

    def _get_traceback(self, exc_info=None):
        "Helper function to return the traceback as a string"
        import traceback
        return '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))

