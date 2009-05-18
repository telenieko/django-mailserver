from django.template import RequestContext as HTTPRequestContext
from django.template import Context

_standard_context_processors = None

def get_standard_processors():
    from mailserver import get_setting
    global _standard_context_processors
    if _standard_context_processors is None:
        processors = []
        for path in get_setting('MAIL_TEMPLATE_CONTEXT_PROCESSORS'):
            i = path.rfind('.')
            module, attr = path[:i], path[i+1:]
            try:
                mod = __import__(module, {}, {}, [attr])
            except ImportError, e:
                raise ImproperlyConfigured('Error importing request processor module %s: "%s"' % (module, e))
            try:
                func = getattr(mod, attr)
            except AttributeError:
                raise ImproperlyConfigured('Module "%s" does not define a "%s" callable request processor' % (module, attr))
            processors.append(func)
        _standard_context_processors = tuple(processors)
    return _standard_context_processors

class RequestContext(HTTPRequestContext):
    def __init__(self, request, dict=None, processors=None):
        Context.__init__(self, dict)
        if processors is None:
            processors = ()
        else:
            processors = tuple(processors)
        for processor in get_standard_processors() + processors:
            self.update(processor(request))

# Processors:
from django.core import context_processors
i18n = context_processors.i18n
media = context_processors.media
request= context_processors.request

