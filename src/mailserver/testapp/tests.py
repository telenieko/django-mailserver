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
Envelope-to: onedest@example.net
Delivery-date: Wed, 22 Oct 2008 10:07:38 -0400
Message-ID: <fab82e500810220403n6d294b91g5ab3963a7fcff7cf@mail.gmail.com>
Date: Wed, 22 Oct 2008 13:03:36 +0200
From: "John Smith" <john@example.com>
To: destination@bugs.example.com
Subject: Prueba GMail plain

Prueba desde GMail en texto llano.

"""

class TestResolver(TestCase):
    def setUp(self):
        self.message = message_from_string(MAIL)
        self.client = Client()

    def test_404(self):
        self.message.replace_header('Envelope-To', 'johndoe@example.org')
        em = EmailRequest(message=self.message)
        try:
            response = self.client.request(em)
        except RecipientNotFound, e:
            self.assertEquals(e.status_code, 551)

    def request_one(self, to):
        self.message.replace_header('Envelope-To', to)
        em = EmailRequest(message=self.message)
        response = self.client.request(em)
        return response

    def test_ok(self):
        response = self.request_one('manolo@bugs.example.com')
        self.assertEquals(response.context['request']['Envelope-To'][1], 'manolo@bugs.example.com')
        self.assertEquals(response.context['sender'], 'manolo')
        


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
        try:
            response = self.client.request(request)
        except RecipientNotFound:
            pass
        user = response.context['user']
        self.assertEquals(False, user.is_anonymous())
        self.assertEquals(user, self.user)
        
        
        
