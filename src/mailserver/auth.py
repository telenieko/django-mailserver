from django.contrib.auth import backends, load_backend
from django.contrib.auth.models import User
from mailserver.exceptions import PermissionDenied

class MailFromBackend(backends.ModelBackend):
    def authenticate(self, request):
        name, mail = request['From']
        try:
            user = User.objects.get(email=mail)
            return user
        except User.DoesNotExist:
            return None

def get_backends():
    from mailserver import get_setting
    backends = []
    for backend_path in get_setting('MAIL_AUTHENTICATION_BACKENDS'):
        backends.append(load_backend(backend_path))
    return backends

def get_user(request):
    from django.contrib.auth.models import AnonymousUser
    user = authenticate(request=request)
    if user is None:
        user = AnonymousUser()
        user.email, user.first_name = request['From']
    return user

def authenticate(**credentials):
    for backend in get_backends():
        try:
            user = backend.authenticate(**credentials)
        except TypeError:
            pass
        if user is None:
            continue
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        return user

class AuthenticationMiddleware(object):
    def process_request(self, request):
        request.user = get_user(request)
        return None

# Decorators
def login_required(view):
    def decorate(request, *args, **kwargs):
        if request.user.is_anonymous():
            raise PermissionDenied(
                "You need to be authenticated to access this resource.")
        return view(request, *args, **kwargs)
    return decorate 
