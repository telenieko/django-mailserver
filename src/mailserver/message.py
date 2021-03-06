import email, re
from email import message_from_string
from string import join
from rfc822 import AddressList, parseaddr
from django.conf import settings
from django.core.files import uploadhandler
from django.utils.datastructures import MultiValueDict
from django.core.mail import EmailMessage


class EmailRequest(object):
    _encoding = None
    _addresses = None
    FILES = None
    META = None

    def __init__(self, message, recipient=None):
        self.message = message
        self._encoding = settings.DEFAULT_CHARSET
        self._addresses = {}
        if recipient is None:
            recipient = self.message['Envelope-To']
        self.recipient = recipient
        self.FILES = MultiValueDict()
        self.META = MultiValueDict()
        self.parse_file_upload()

    def __repr__(self):
        attached = ["\n\tAttachment: %s" % \
            file.name for k, file in self.FILES.iteritems()]
        attached = join(attached, '')
        return u"<EmailRequest\n\tFrom: %s\n\tTo: %s%s>" % \
            (self['From'], self.get_recipient(), attached)

    def __getitem__(self, key):
        lkey = key.lower()
        if not self.message.has_key(key):
            raise AttributeError, "%s has no such key %s" % (repr(self), key)
        if lkey in ['to', 'bcc', 'cc']:
            adrs = self.get_addresslist(lkey)
            return adrs
        elif lkey in ['from', 'envelope-to']:
            return parseaddr(self.message[lkey])
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
        envelope = parseaddr(self.recipient)
        return envelope
    
    def get_recipient_address(self):
        return self.get_recipient()[1]
    
    get_full_path = get_recipient_address

    def get_recipient_display(self):
        rec = self.recipient
        return rec

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
            txtbody = None
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
    def from_message_data(cls, message, recipient=None):
        msg = message_from_string(message)
        if not recipient:
            recipient = msg['Envelope-To']
        email = cls(msg, recipient)
        return email


class EmailResponse(EmailMessage):
    status_code = 200


class EmailIgnoreResponse(EmailResponse):
    """ Use this to not send any mails and do not say anything
        to the MTAs. """

