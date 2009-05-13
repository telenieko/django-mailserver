import email, re
from email import message_from_string
from string import join
from rfc822 import AddressList
from django.conf import settings
from django.core.files import uploadhandler
from django.utils.datastructures import MultiValueDict
from django.core.mail import EmailMessage


class EmailRequest(object):
    _encoding = None
    _addresses = None
    FILES = None
    META = None

    def __init__(self, message):
        self.message = message
        self._encoding = settings.DEFAULT_CHARSET
        self._addresses = {}
        self.FILES = MultiValueDict()
        self.META = MultiValueDict()
        self.parse_file_upload()

    def __repr__(self):
        attached = ["\n\tAttachment: %s" % \
            file.name for k, file in self.FILES.iteritems()]
        attached = join(attached, '')
        return u"<EmailRequest\n\tFrom: %s\n\tTo: %s%s\nBody:\n%s>" % \
            (self['From'], self.get_recipient(), attached, self.get_body())

    def __getitem__(self, key):
        lkey = key.lower()
        if lkey in ['from', 'to', 'bcc', 'cc', 'envelope-to']:
            adrs = self.get_addresslist(lkey)
            if lkey == 'from': return adrs[0]
            return adrs
        if not self.message.has_key(key):
            raise AttributeError, "%s has no such key %s" % (repr(self), key)
        return self.message[key]

    def get_addresslist(self, field):
        """ Return the value of the header ``field`` converted into
            a rfc822.AddressList()
        """
        field = field.lower()
        if not self._addresses.get(field):
            val = AddressList(self.message[field])
            self._addresses[field] = val
        return self._addresses[field]

    def get_recipient(self):
        """ TODO: Think more about it, it's likely we could end up
            processing the same message either more than once,
            or skipping recipients. Examples:
                * Using an Exim pipe transport matching a subdomain,
                  if we have multiple To, CC or Bcc to us, the message
                  gets delivered only once unless exim is told otherwise.
                * We could get one copy for each To, CC and Bcc address to
                  us, and we could end up processing the message all those
                  times.
        """
        # Best of all is "Envelope-To" which gets added by MTA on delivery.
        envelope = self['Envelope-To']
        if len(envelope) == 1:
            return envelope[0]
        raise ValueError, "Could not get recipient for %s" % self
    
    def get_recipient_address(self):
        return self.get_recipient()[1]

    def get_recipient_display(self):
        rec = self.get_recipient()
        realname = u''
        if rec[0] != '':
            realname = u"%s " % rec[0]
        return u"%s<%s>" % (realname, rec[1])

    def get_body(self):
        """ Get the body of a Message, it can either be:
                * The payload of a non-MIME message.
                * The first text/plain inline part.
                * The last text/html inline part.
            In this order.
        """
        def m2decode(msg):
            """ From drupal's mail2ticket.py """
            charset = msg.get_charsets()[0]
            if charset != None:
                try:
                    txt = msg.get_payload(decode=True).decode(charset)
                except:
                    try:
                        txt = msg.get_payload(decode=True).decode(_encoding)
                    except:
                        txt = msg.get_payload(decode=True).decode('utf8', 'replace')
            else:
                try:
                    txt = msg.get_payload(decode=True).decode(_encoding)
                except:
                    try:
                        txt = msg.get_payload(decode=True).decode('utf8', 'replace')
                    except:
                        return None
            return txt
        txtbody = None
        htmlbody = None
        msg = self.message
        if msg.is_multipart():
            for payload in msg.get_payload():
                if payload.get_filename() is None:
                    if payload.get_content_maintype() == 'text':
                        if payload.get_content_subtype() == 'plain':
                            txtbody = m2decode(payload)
                            break
                        elif payload.get_content_subtype() == 'html':
                            htmlbody = m2decode(payload)
                        else:
                            raise ValueError("Unkown inline payload type: text/%s" % payload.get_subtype())
        else:
            txtbody = m2decode(msg)
        if not txtbody and not htmlbody:
            raise ContentNotFound, "No body was present"
        elif htmlbody is not None:
            # TODO: convert htmlbody to TXT.
            raise NotImplementedError("HTML>TXT Conversion not yet ready")
        return txtbody

    def parse_file_upload(self):
        """ Put files that were attached to self.FILES using
            standard Django upload handlers. """
        upload_handlers = [uploadhandler.load_handler(handler, self)
                           for handler in settings.FILE_UPLOAD_HANDLERS]
        if not self.message.is_multipart():
            return []
        for payload in self.message.get_payload():
            if payload.get_filename() is None:
                continue
            field_name = "--"
            file_name = payload.get_filename()
            content_type = payload.get_content_type()
            charset = payload.get_content_charset()
            content = payload.get_payload(decode=True)
            content_length = len(content)
            #import pdb; pdb.set_trace()
            try:
                for handler in upload_handlers:
                    result = handler.handle_raw_input(content, {},
                        content_length, None, charset)
                    if result is not None:
                        file_obj = handler.file_complete(content_length)
                        self.FILES.appendlist(field_name, file_obj)
                        continue
                    try:
                        handler.new_file(field_name, file_name,
                                         content_type, content_length,
                                         charset)
                    except uploadhandler.StopFutureHandlers:
                        break
                for handler in upload_handlers:
                    try:
                        chunk = handler.receive_data_chunk(content, 0)
                        if chunk is None:
                            file_obj = handler.file_complete(content_length)
                            self.FILES.appendlist(field_name, file_obj)
                            break
                    except:
                        raise
            except uploadhandler.SkipFile, e:
                raise
        for handler in upload_handlers:
            retval = handler.upload_complete()
            if retval:
                break
        # TODO: To free memory we could now remove those payloads from
        # self.message

    @classmethod
    def from_message_data(cls, message):
        msg = message_from_string(message)
        email = cls(msg)
        return email


class EmailResponse(EmailMessage):
    status_code = 200


class EmailIgnoreResponse(EmailResponse):
    """ Use this to not send any mails and do not say anything
        to the MTAs. """


class EmailResponseServer(EmailResponse):
    """ Use this for responses that should be given back
        to MTA's (i.e. Recipient Not Found). """
    pass


class EmailResponseNotFound(EmailResponseServer):
    status_code = 551

