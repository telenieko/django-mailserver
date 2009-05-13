import re
from django.utils.functional import memoize
from django.utils.datastructures import MultiValueDict
from mailserver.exceptions import RecipientNotFound, MailerDoesNotExist
from django.core import urlresolvers
from django.utils.encoding import smart_str

Resolver404 = urlresolvers.Resolver404

_resolver_cache = {} # Maps mailconf modules to RegexURLResolver instances.

def get_resolver(mailconf):
    if mailconf is None:
        from django.conf import settings
        mailconf = settings.ROOT_EMAILCONF
    return RegexMailResolver(r'', mailconf)
get_resolver = memoize(get_resolver, _resolver_cache, 1)


class RegexMailPattern(urlresolvers.RegexURLPattern):
    pass


class RegexMailResolver(urlresolvers.RegexURLResolver):
    def resolve(self, path):
        # There is only one change here from the original...
        # the "sub" call.
        tried = []      
        match = self.regex.search(path)
        if match:           
            new_path = self.regex.sub('', path)
            for pattern in self.urlconf_module.urlpatterns:
                try:
                    sub_match = pattern.resolve(new_path)
                except Resolver404, e:
                    tried.extend([(pattern.regex.pattern + '   ' + t) for t in e.args[0]['tried']])
                else:
                    if sub_match:
                        sub_match_dict = dict([(smart_str(k), v) for k, v in match.groupdict().items()])
                        sub_match_dict.update(self.default_kwargs)
                        for k, v in sub_match[2].iteritems():
                            sub_match_dict[smart_str(k)] = v
                        return sub_match[0], sub_match[1], sub_match_dict
                    tried.append(pattern.regex.pattern)
            raise Resolver404, {'tried': tried, 'path': new_path}


def resolve(path, mailconf=None):
    return get_resolver(mailconf).resolve(path)

def reverse(viewname, mailconf=None, args=None, kwargs=None):
    args = args or []
    kwargs = kwargs or {}
    return iri_to_uri(u'%s%s' % (prefix, get_resolver(mailconf).reverse(viewname,
            *args, **kwargs)))

