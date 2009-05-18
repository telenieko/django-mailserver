# -*- coding: UTF-8 -*-
from django.http import Http404

class DeliveryError(Exception):
    status_code = -1

class RecipientNotFound(DeliveryError):
    status_code = 551
    pass

class MailerDoesNotExist(RecipientNotFound):
    pass

class ContentNotFound(DeliveryError):
    pass
