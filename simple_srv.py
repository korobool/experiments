import asyncio
import aiorest
import json

def leadinga(request, **kwargs):
    try:
        jo = request.json_body
    except ValueError:    
        return {'error': '10'}
    
    for k in request.args:
        print("k: " + request.args[k])
    
    words = [val for key, val in jo.items() if val.startswith('a')]

    return json.JSONEncoder().encode({'words':words})
    
loop = asyncio.get_event_loop()
srv = aiorest.RESTServer(hostname='127.0.0.1',loop=loop)

srv.add_url('POST', '/leadinga', leadinga, True)
server = loop.run_until_complete(loop.create_server(
    srv.make_handler, '127.0.0.1', 8080))

try:
    loop.run_forever()
except KeyboardInterrupt:
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
