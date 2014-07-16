import asyncio
import aiorest
import json

from inspect import signature
from inspect import ismethod


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
                         if ismethod(getattr(self.obj, method))
                         and not method.startswith("_")}

    def _build_schema(self, sig):
        schema = {}
        pos = []
        if sig.parameters:
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
            jo = request.json_body
            schema = self.schema[name]

            if not jo.keys() == schema.keys():
                raise ValueError("Keys doesn't match schema")

            if jo:
                for key, value in jo.items():
                    if (key == 'args' and not isinstance(value, list)):
                        raise ValueError("Wrong type for *args")
                    if (key == 'kwargs' and not isinstance(value, dict)):
                        raise ValueError("Wrong type for **kwargs")
                    if (key == 'pos' and not isinstance(value, list)):
                        raise ValueError("Wrong type for positional")
                    if (key == 'pos' and not len(value) == len(schema[key])):
                        raise ValueError("Positional arguments missmatch")

                args.extend(jo['pos'])
                args.extend(jo['args'])
                kwargs = jo['kwargs']
 
            ba = sig.bind(*args, **kwargs)
        except ValueError as e:
            raise aiorest.RESTError(400, "Bad Request", {'msg': str(e)})
        return ba

    def _wrap_response(self, response):
        return {'response': response}

    def _build_routes(self):
        for name, method in self._methods.items():
            sig = signature(method)
            self.schema.update({name: self._build_schema(sig)})

            def fn(request, name=name):   # and what about GET without request?
                method = self._methods[name]
                sig = signature(self._methods[name])
                ba = self._make_arguments(request, name, sig)
                return self._wrap_response(method(*ba.args, **ba.kwargs))

            self.srv.add_url('POST', '/' + name, fn, True)

        def api():
            return self._wrap_response(self.schema)
                       
        self.srv.add_url('GET', '/_api', api, False)
