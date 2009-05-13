# -*- coding: UTF-8 -*-
from django.http import Http404

class RecipientNotFound(Http404):
    pass

class MailerDoesNotExist(RecipientNotFound):
    pass

class ContentNotFound(Exception):
    pass
