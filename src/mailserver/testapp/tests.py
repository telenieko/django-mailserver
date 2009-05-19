import unittest
import os, sys

from email import message_from_string
from django.test import TestCase
from django.template import TemplateDoesNotExist
from django.contrib.auth.models import User, AnonymousUser
from mailserver import *
from mailserver.handlers import BaseMessageHandler
from mailserver.test import Client
from mailserver.exceptions import *

MAIL = """From jerry@example.com Wed Oct 22 07:16:19 2008
Return-path: <tom@example.com>
Envelope-to: destination@example.com
Delivery-date: Wed, 22 Oct 2008 10:07:38 -0400
Message-ID: <fab82e500810220403n6d294b91g5ab3963a7fcff7cf@mail.gmail.com>
Date: Wed, 22 Oct 2008 13:03:36 +0200
From: "John Smith" <john@example.com>
To: to-destination@example.com
Subject: Prueba GMail plain

Prueba desde GMail en texto llano.

"""

class TestMiddleware(object):
    def process_request(self, request):
        request.middlewares = {}
        request.middlewares['request'] = True

    def process_view(self, request, callback, args, kwargs):
        request.middlewares['view'] = True

    def process_response(self, request, response):
        request.middlewares['response'] = True
        return response

    def process_exception(self, request, e):
        request.middlewares['exception'] = True


class TestResolver(TestCase):
    def setUp(self):
        self.message = message_from_string(MAIL)
        self.client = Client()

    def test_404(self):
        self.message.replace_header('Envelope-To', 'johndoe@example.org')
        em = EmailRequest(message=self.message)
        response = self.client.request(em)
        self.assertEquals('recipient_notfound.txt', response.template.name)

    def test_ok(self):
        em = EmailRequest(message=self.message)
        response = self.client.request(em)
        self.assertEquals(
            response.context['request'].get_recipient_address(),
            'destination@example.com')
        self.assertEquals(response.subject, 'Echo Echo')


class TestHandler(TestCase):
    def setUp(self):
        self.message = message_from_string(MAIL)


class TestRequest(TestCase):
    def setUp(self):
        self.message = message_from_string(MAIL)

    def test_requestcontext(self):
        from mailserver.context import RequestContext
        current_processors = get_setting('MAIL_TEMPLATE_CONTEXT_PROCESSORS')
        assert 'mailserver.context.request' in current_processors
        request = EmailRequest(message=self.message)
        context = RequestContext(request)
        assert context['request'] == request

    def test_req_middleware(self):
        current_middleware = get_setting('MAIL_MIDDLEWARE')
        settings.MAIL_MIDDLEWARE = current_middleware + ('testapp.tests.TestMiddleware', )
        request = EmailRequest(message=self.message)
        client = Client()
        response = client.request(request)
        self.assertEquals(True, request.middlewares['request'])
        self.assertEquals(True, request.middlewares['view'])
        self.assertEquals(True, request.middlewares['response'])
        settings.MAIL_MIDDLEWARE = current_middleware

    def test_exc_middleware(self):
        self.message.replace_header('Envelope-To', 'except@example.com')
        current_middleware = get_setting('MAIL_MIDDLEWARE')
        settings.MAIL_MIDDLEWARE = current_middleware + ('testapp.tests.TestMiddleware', )
        request = EmailRequest(message=self.message)
        client = Client()
        self.assertRaises(DeliveryError, client.request, request)
        self.assertEquals(True, request.middlewares['exception'])
        settings.MAIL_MIDDLEWARE = current_middleware


class TestAuthentication(TestCase):
    def setUp(self):
        self.message = message_from_string(MAIL)
        self.user = User.objects.create_user('Bob', 'bob@example.com', '123')
        self.client = Client()

    def test_anonymous(self):
        request = EmailRequest(message=self.message)
        try:
            response = self.client.request(request)
        except RecipientNotFound:
            pass
        user = response.context['user']
        self.assertEquals(True, user.is_anonymous())
        
    def test_registered(self):
        self.message.replace_header('From', 'bob@example.com')
        request = EmailRequest(message=self.message)
        response = self.client.request(request)
        user = response.context['user']
        self.assertEquals(False, user.is_anonymous())
        self.assertEquals(user, self.user)

    def test_loginrequired_anonymous(self):
        self.message.replace_header('Envelope-To', 'login@example.com')
        request = EmailRequest(message=self.message)
        response = self.client.request(request)
        self.assertEquals('Access Denied to Recipient', response.subject)

    def test_loginrequired_registered(self):
        self.message.replace_header('From', 'bob@example.com')
        self.message.replace_header('Envelope-To', 'login@example.com')
        request = EmailRequest(message=self.message)
        response = self.client.request(request)
        self.assertEquals('Echo Echo', response.subject)

