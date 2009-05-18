from django.test import client
from mailserver.handlers import BaseMessageHandler
from django.test import signals
from django.utils.functional import curry

class Client(client.Client):
    def __init__(self, **defaults):
        client.Client.__init__(self, **defaults)
        self.handler = BaseMessageHandler()

    def request(self, request):
        environ = { }
        environ.update(self.defaults)

        # curry a data dictionary into an instance of the template renderer
        # callback function.
        data = {}
        on_template_render = curry(client.store_rendered_templates, data)
        signals.template_rendered.connect(on_template_render)

        ## capture exceptions created by the handler.
        #got_request_exception.connect(self.store_exc_info)

        response = self.handler(environ, request)

        if self.exc_info:
            exc_info = self.exc_info
            self.exc_info = none
            raise exc_info[1], none, exc_info[2]

        # save the client and request that stimulated the response.
        response.client = self
        response.request = request

        # add any rendered template detail to the response.
        # if there was only one template rendered (the most likely case),
        # flatten the list to a single element.
        for detail in ('template', 'context'):
            if data.get(detail):
                if len(data[detail]) == 1:
                    setattr(response, detail, data[detail][0]);
                else:
                    setattr(response, detail, data[detail])
            else:
                setattr(response, detail, None)

        return response

