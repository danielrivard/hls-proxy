import logging
from base64 import urlsafe_b64decode
from typing import Iterable

import falcon
from gevent import pywsgi

from proxy import hls_proxy

logging.basicConfig(level=logging.DEBUG)


class HlsProxyApi:
    def on_get(self, req: falcon.Request, res: falcon.Response, path: str, extension: str):
        # Add padding just in case
        url = urlsafe_b64decode(path + '====')

        response = hls_proxy(url, extension)

        if isinstance(response.body, Iterable):
            res.stream = response.body
        elif isinstance(response.body, bytes):
            res.data = response.body
        else:
            res.text = response.body

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
