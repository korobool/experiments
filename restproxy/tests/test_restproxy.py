import urllib2
import json
import asyncio
import aiorest
import restproxy
import unittest


class NiftyClass(object):

    def __init__(self):
        pass

    def _private_1(self, arg):
        return "private_1"

    def public_first(self):
        return "first"

    def public_second(self, arg):
        return "second"

    def public_third(self, *args):
        return "third"

    def public_fourth(self, a, b, *args, **kwargs):
        print("fourth a:{} b:{} *args:{} **kwargs:{}"
              .format(a, b, args, kwargs))
        return "fourth"

class TestRESTProxy(unittest.TestCase):

    def run_server():
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

    def post(path, data):
        req = urllib2.Request('http://127.0.0.1:8080/'+ path)
        req.add_header('Content-Type', 'application/json')
        return urllib2.urlopen(req, json.dumps(data)) 
        
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_equal(self):
        self.assertEqual(1,1)

    def test_except(self):
        with self.assertRaises(ValueError):
            pass

if __name__ == '__main__':
    unittest.main()
