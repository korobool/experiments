import asyncio
import aiorest
import json
import jsonschema

from inspect import signature


class NiftyClass(object):

    def __init__(self):
        pass

    def _private_first(self, arg):
        pass

    def public_first(self):
        pass

    def public_second(self, arg):
        pass

    def public_third(self, *args):
        pass

    def public_fourth(self, **kwargs):
        pass


class RESTProxy(object):

    def __init__(self, obj, srv):
        self.obj = obj
        self.srv = srv
        self._get_methods()
        self._build_routes()

    def _get_methods(self):
        self._methods = {method: getattr(self.obj, method)
                         for method in dir(self.obj)
                         if callable(getattr(self.obj, method))
                         and not method.startswith("_")}

    def _make_arguments(self, request, method):
        sig = inspect.signature(method)
        params = sig.parameters
        # validate and convert json fields to signature
        # validate with jsonschema?
        try:
            j = request.json_body
        except ValueError:
            raise

        return sig.bind(###)

    def _wrap_response(self, response):
        return json.dumps(response, default=lambda o: o.__dict__)

    def _build_routes(self):
        for name, method in self._methods.items:

            def fn(request):    # and what about GET without request?
                if ba = self._make_arguments(request, method):
                    return self._wrap_response(method(*ba.args, **ba.kwargs))
                return {} # XXX
            
            if inspect.signature(method).parameters:
                # should generate JSON schema here?
                # for each method signature
                self.srv.add_url('POST', name, fn, True)
            else
                self.srv.add_url('GET', name, fn, False)

if __name__ == "__main__":

    obj = NiftyClass()
    loop = asyncio.get_event_loop()
    srv = aiorest.RESTServer(hostname='127.0.0.1', loop=loop)

    proxy = RESTProxy(obj, srv)

    server = loop.run_until_complete(loop.create_server(
        srv.make_handler, '127.0.0.1', 8080))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

