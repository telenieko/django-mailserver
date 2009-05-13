Develop Mailservices in Django
==============================

Django Mailserver is an application that lets you develop
mail services in your Django projects/applications in a manner
that handles messages as Django handles HTTP requests.

That project was initialy conceived as an improvement over
`django-smtpd`_ by Denis Laprise, then became an almost full rewrite
and when I thought I had gone through almost every line of code it
seemed far much more like a fork than improvement.

NOTE: that this is really alpha software, don't use it in a production
environment unless you expect it to break everything ;)

.. _django-smtpd: http://code.google.com/p/django-smtpd/

Example usage:
==============

First of all, you need to add "mailserver" in your INSTALLED_APPS, and
you'll want the settings::

    ROOT_MAILCONF = 'myproject.mailbox' # Just like ROOT_URLCONF, but for
                                        # resolving recipients.
    MAILER_DAEMON_ADDRESS = 'postmaster@mydomain.com'

``ROOT_MAILCONF`` is just like an URLCONF, but it matches e-mail addresses
instead of paths. An example ``myproject.mailbox`` ``mailbox.py`` file
would be::

    from django_mailserver.mailbox import *

    urlpatterns = patterns('',
      (r'@bugs.example.com', include('myapp.mailbox')),
    )

Note, that when matching recipients, just as Django strips path elements
as they get matches, ``mailserver`` strips already matched parts from
the addresses until it reaches the views.

Now you can start you mail service! You can either to::

    ./manage.py startmailapp <app_name>

From your project directory to have a new app created with a sample mailbox.py
file in it, or you can create a new mailbox.py file in your existing application::

    from django_mailserver.mailbox import *

    urlpatterns = patterns('',
      (r'^onedest', 'myapp.mailers.reply'),
    )

You have it, your ``mailers.py`` file would be just like a ``views.py``::

    from mailserver import EmailResponse

    def reply(request):
        print "Got email %s, Reply!" % request
        return EmailResponse(
                from_email=request.get_recipient_display(),
                to=request['From'],
                body=request.get_body(),
                subject="Re: %s" % request['Subject'])
        
You get the idea, if you return an EmailResponse it gets ``send()``
later by the Handler. You can also return EmailIgnoreResponse among others.

Delivering mails
****************

Right now the only possible way to deliver messages to this is through a
pipe transport to the ``./manage.py readmail`` command. Which is mostly
intended for testing.

Further improvements should have a more performant pipe transport and a
self-running SMTP server.

TODO
****

**WARNING:** Django Mailserver is still under development. It is believed to
brake at any point ;) There are lots of things to do, like:

    * Documentation
    * More tests.
    * Better URL parsing (i.e: includes work on domains, others on addreses).
    * Handling address prefixes/suffixes
    * Handling of error responses (ie: pipe transport should bring the
      response status_code to the exit value of the process).

