import asyncio
import aiorest
import json

from inspect import signature


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
        schema = {}
        pos = []
        for name, param in sig.parameters.items():
            if (param.kind == param.VAR_KEYWORD):
                schema.update({'kwargs': {}})
            elif (param.kind == param.VAR_POSITIONAL):
                schema.update({'args': []})
            else:
                pos.append(name)

        schema.update({'pos': pos})
        return schema

    def _make_arguments(self, request, name, sig):
        try:
            args = []
            kwargs = {}
            json = request.json_body
            schema = self.schema[name]

            if not json.keys() == schema.keys():
                raise TypeError("Keys doesn't match schema.")

            for key, value in json.items():
                if (key == 'args' and not isinstance(value, list)):
                    raise TypeError("Wrong type for *args.")
                if (key == 'kwargs' and not isinstance(value, dict)):
                    raise TypeError("Wrong type for **kwargs.")
                if (key == 'pos' and not isinstance(value, list)):
                    raise TypeError("Wrong type for positional.")
                if (key == 'pos' and not len(value) == len(schema[key])):
                    raise TypeError("Positional arguments missmatch.")

            args.extend(json['pos'])
            args.extend(json['args'])
            kwargs = json['kwargs']
            ba = sig.bind(*args, **kwargs)

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

            def fn(request, name=name):   # and what about GET without request?
                method = self._methods[name]
                sig = signature(self._methods[name])
                ba = self._make_arguments(request, name, sig)
                if ba:
                    return self._wrap_response(method(*ba.args, **ba.kwargs))
                return {}

            if sig.parameters:
                self.srv.add_url('POST', '/' + name, fn, True)
            else:
                self.srv.add_url('GET', '/' + name, fn, False)

        def api():
            return self._wrap_response(self.schema)
                       
        self.srv.add_url('GET', '/_api', api, False)
