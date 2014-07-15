import asyncio
import aiorest
import json
import jsonschema

from inspect import signature
from collections import OrderedDict


class NiftyClass(object):

    def __init__(self):
        pass

    def _private_first(self, arg):
        return "private_first" 

    def public_first(self):
        return "first"

    def public_second(self, arg):
        return "second"

    def public_third(self, *args):
        return "third"

    def public_fourth(self, a, b, *args, **kwargs):
        print("fourth a:{} b:{} *args:{} **kwargs:{}".format(a,b,args,kwargs))
        return "fourth"


class RESTProxy(object):

    def __init__(self, obj, srv):
        self.obj = obj
        self.srv = srv
        self.schema = {}
        self._get_methods()
        self._build_routes()

    def _get_methods(self):
        self._methods = {method: getattr(self.obj, method)
                         for method in dir(self.obj)
                         if callable(getattr(self.obj, method))
                         and not method.startswith("_")}

    def _build_schema(self, sig):
        ord = OrderedDict()
        for name, param in sig.parameters.items():
            if (param.kind == param.VAR_KEYWORD):
                ord.update({name: {"type": "object"}})
            elif (param.kind == param.VAR_POSITIONAL):
                ord.update({name: {"type": "array"}})
            else:
                ord.update({name: {"anyOf": [{"type": "string"},
                                             {"type": "number"}]}})
            return json.loads('{{"type": "object", "properties": {}}}'
                              .format(json.dumps(ord)),
                              object_pairs_hook=OrderedDict)

    def _make_arguments(self, request, name, sig):
        try:
            j = request.json_body
            jsonschema.validate(j, self.schema[name])
            args = []
            kwargs = {}
            for value in j.values():
                print("value:{} class: {}".format(value,value.__class__))
                if isinstance(value, list):
                    args.extend(value)
                elif isinstance(value, OrderedDict):
                    kwargs = dict(value)
                else:
                    args.append(value)
            ba = sig.bind(*args, **kwargs)

        except jsonschema.ValidationError as e:
            print(e.message)
        except jsonschema.SchemaError as e:
            print(e)
        except ValueError:
            raise
        except TypeError:
            raise

        return ba

    def _wrap_response(self, response):
        return json.dumps(response, default=lambda o: o.__dict__)

    def _build_routes(self):
        for name, method in self._methods.items():
            sig = signature(method)
            self.schema.update({name: self._build_schema(sig)})

            def fn(request, name=name):    # and what about GET without request?
                method = self._methods[name]
                sig = signature(self._methods[name])
                ba = self._make_arguments(request, name, sig)
                if ba:
                    return self._wrap_response(method(*ba.args, **ba.kwargs))
                return {}       # XXX

            if sig.parameters:
                # should generate JSON schema here?
                # for each method signature
                self.srv.add_url('POST', '/' + name, fn, True)
            else:
                self.srv.add_url('GET', '/' + name, fn, False)

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
