# -*- coding: UTF-8 -*-
from django.http import Http404

class DeliveryError(Exception):
    # Persistent Transeint Failures start with '4'
    status_code = 400

class PermanentDeliveryError(DeliveryError):
    # Permanent Failures start with '5'
    status_code = 500

class PermissionDenied(PermanentDeliveryError):
    status_code = 530
    
class RecipientNotFound(PermanentDeliveryError):
    status_code = 511

class MailerDoesNotExist(RecipientNotFound):
    pass

class ContentNotFound(DeliveryError):
    pass

