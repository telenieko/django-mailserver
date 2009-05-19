from mailserver import resolvers
from mailserver.exceptions import *
from mailserver import EmailResponse, EmailIgnoreResponse
from threading import Lock
import logging
import sys

class BaseMessageHandler(object):
    initLock = Lock()

    def __init__(self):
        self._request_middleware = self._view_middleware = self._response_middleware = self._exception_middleware = None

    def __call__(self, environ, request):
        if self._request_middleware is None:
            self.initLock.acquire()
            if self._request_middleware is None:
                self.load_middleware()
            self.initLock.release()
        resp = self.get_response(request)
        # Need to handle when the reply is to be sent
        # Or needs to not mark-as-delivered
        if isinstance(resp, EmailIgnoreResponse):
            pass
        elif isinstance(resp, EmailResponse):
            # Some kind of normal response, we send to the user.
            resp.send()
        else:
            raise ValueError, "Do not know how to handle response %s" % resp
        return resp
      
    def __repr__(self):
        return self.__class__.__name__

    def load_middleware(self):
        """
        Populate middleware lists from settings.MAIL_MIDDLEWARE_CLASSES.
        """
        from django.core import exceptions
        from mailserver import get_setting
        self._view_middleware = []
        self._response_middleware = []
        self._exception_middleware = []

        request_middleware = []
        for middleware_path in get_setting('MAIL_MIDDLEWARE'):
            try:
                dot = middleware_path.rindex('.')
            except ValueError:
                raise exceptions.ImproperlyConfigured, '%s isn\'t a middleware module' % middleware_path
            mw_module, mw_classname = middleware_path[:dot], middleware_path[dot+1:]
            try:
                mod = __import__(mw_module, {}, {}, [''])
            except ImportError, e:
                raise exceptions.ImproperlyConfigured, 'Error importing middleware %s: "%s"' % (mw_module, e)
            try:
                mw_class = getattr(mod, mw_classname)
            except AttributeError:
                raise exceptions.ImproperlyConfigured, 'Middleware module "%s" does not define a "%s" class' % (mw_module, mw_classname)

            try:
                mw_instance = mw_class()
            except exceptions.MiddlewareNotUsed:
                continue

            if hasattr(mw_instance, 'process_request'):
                request_middleware.append(mw_instance.process_request)
            if hasattr(mw_instance, 'process_view'):
                self._view_middleware.append(mw_instance.process_view)
            if hasattr(mw_instance, 'process_response'):
                self._response_middleware.insert(0, mw_instance.process_response)
            if hasattr(mw_instance, 'process_exception'):
                self._exception_middleware.insert(0, mw_instance.process_exception)

        # We only assign to this when initialization is complete as it is used
        # as a flag for initialization being complete.
        self._request_middleware = request_middleware

    def get_response(self, request):
        from django.core import exceptions
        from mailserver import get_setting

        # Apply request middleware
        for middleware_method in self._request_middleware:
            response = middleware_method(request)
            if response:
                return response

        mailconf = getattr(request, "mailconf", get_setting('ROOT_MAILCONF'))
        resolver = resolvers.RegexMailResolver(r'', mailconf)
        try:
            callback, callback_args, callback_kwargs = \
                resolver.resolve(request.get_recipient_address())
            # Apply view middleware
            for middleware_method in self._view_middleware:
                response = middleware_method(request, callback, callback_args, callback_kwargs)
                if response:
                    return response

            try:
                response = callback(request, *callback_args, **callback_kwargs)
            except Exception, e:
                for middleware_method in self._exception_middleware:
                    response = middleware_method(request, e)
                    if response:
                        return response
                raise
            # Complain if the view returned None (a common error).
            if response is None:
                try:
                    view_name = callback.func_name
                except AttributeError:
                    view_name = callback.__class__.__name__ + '.__call__'
                raise ValueError, "The view %s.%s didn't return a meaningfull response" % (callback.__module__, view_name)
            return response
        except SystemExit:
            raise
        except:
            exc_info = sys.exc_info()
            exc = exc_info[1]
            if hasattr(exc, 'get_response'):
                response = exc.get_response(request)
                if response is not None:
                    return response
            self.handle_uncaught_exception(request, resolver, exc_info)
        return response
            
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

    def _get_traceback(self, exc_info=None):
        "Helper function to return the traceback as a string"
        import traceback
        return '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))

