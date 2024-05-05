import logging
from base64 import urlsafe_b64decode

import falcon
from gevent import pywsgi

from proxy import hls_proxy

logging.basicConfig(level=logging.DEBUG)


class HlsProxyApi:
    def on_get(self, req: falcon.Request, res: falcon.Response, path: str, extension: str):
        # Add padding just in case
        url = urlsafe_b64decode(path + '====')

        response = hls_proxy(url, extension)
        t = type(response.body)
        if isinstance(response.body, (str, bytes, bytearray)):
            res.data = response.body
        else:
            res.stream = response.body
        res.status = response.status
        res.content_type = response.content_type
        {res.append_header(k, v) for k, v in response.headers.items()}


app = falcon.App()
proxy = HlsProxyApi()
app.add_route('/{path}.{extension}', proxy)


if __name__ == '__main__':
    port = 8000
    server = pywsgi.WSGIServer(("localhost", port), app)
    server.serve_forever()
