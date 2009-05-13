from mailserver.resolvers import RegexMailResolver, RegexMailPattern
from django.core.exceptions import ImproperlyConfigured

__all__ = ['handler404', 'handler500', 'include', 'patterns', 'mailbox']

handler404 = 'mailserver.mailers.page_not_found'
handler500 = 'mailserver.mailers.server_error'

include = lambda mailconf_module: [mailconf_module]

def patterns(prefix, *args):
    pattern_list = []
    for t in args:
        if isinstance(t, (list, tuple)):
            t = mailbox(prefix=prefix, *t)
        elif isinstance(t, RegexMailPattern):
            t.add_prefix(prefix)
        pattern_list.append(t)
    return pattern_list

def mailbox(regex, mailer, kwargs=None, name=None, prefix=''):
    if type(mailer) == list:
        # For include(...) processing.
        return RegexMailResolver(regex, mailer[0], kwargs)
    else:
        if isinstance(mailer, basestring):
            if not mailer:
                raise ImproperlyConfigured('Empty mailbox pattern mailer name not permitted (for pattern %r)' % regex)
            if prefix:
                mailer = prefix + '.' + mailer
        return RegexMailPattern(regex, mailer, kwargs, name)
