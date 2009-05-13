import unittest
import os, sys
from email import message_from_string
from django.test import TestCase
from mailserver import *
from mailserver.handlers import BaseMessageHandler

MAIL = """From marc@telenieko.com Wed Oct 22 07:16:19 2008
Return-path: <marc@telenieko.com>
Envelope-to: pybts@bugs.example.com
Delivery-date: Wed, 22 Oct 2008 10:07:38 -0400
Message-ID: <fab82e500810220403n6d294b91g5ab3963a7fcff7cf@mail.gmail.com>
Date: Wed, 22 Oct 2008 13:03:36 +0200
From: "Marc Fargas Esteve" <marc@telenieko.com>
To: submit@bugs.example.com
Subject: Prueba GMail plain

Prueba desde GMail en texto llano.

"""

class TestResolver(TestCase):
    def setUp(self):
        self.message = message_from_string(MAIL)

    def test_404(self):
        self.message.replace_header('Envelope-To', 'johndoe@example.org')
        em = EmailRequest(message=self.message)
        handler = BaseMessageHandler()
        res = handler(os.environ, em)
        assert isinstance(res, EmailResponseNotFound)

    def handle_for(self, to):
        self.message.replace_header('Envelope-To', to)
        em = EmailRequest(message=self.message)
        handler = BaseMessageHandler()
        return handler(os.environ, em)

    def test_includes(self):
        res = self.handle_for('somebody@example.net')
        self.assertEquals(res.sender, 'somebody')
        self.assertEquals(res.domain, '')
        res = self.handle_for('somebody@myapp.example.net')
        self.assertEquals(res.sender, 'somebody')
        self.assertEquals(res.domain, 'myapp')
        res = self.handle_for('somebody@myapp.example.net')
        self.assertEquals(res.sender, 'somebody')
        self.assertEquals(res.domain, 'myapp')

class TestHandler(TestCase):
    def setUp(self):
        self.message = message_from_string(MAIL)
    
