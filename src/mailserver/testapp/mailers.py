from mailserver import EmailResponse, EmailIgnoreResponse, EmailResponseServer

def echo(request, sender, domain=None):
    print 'received sender=%s domain=%s' % (sender, domain)
    resp = EmailResponseServer(from_email=request.get_recipient_display(),
        to=request['From'], body=sender,
        subject="Echo Echo")
    resp.sender = sender
    resp.domain = domain
    return resp

def reply(request):
    print "Got email %s, mirror-reply!" % request
    return EmailResponse(from_email=request.get_recipient_display(),
            to=request['From'],
            body=request.get_body(),
            subject="Re: %s" % request['Subject'])
