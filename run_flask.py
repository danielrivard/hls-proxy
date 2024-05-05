import logging
from base64 import urlsafe_b64decode
from datetime import timedelta

from flask import Flask, Response
from flask_caching import Cache
from flask_compress import Compress
from gevent import pywsgi

from proxy import hls_proxy

logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)

Compress(app)
app.config['COMPRESS_MIMETYPES'].append('application/x-mpegURL')


# Optional key endpoint for caching
# @app.route('/<string:path>.key')
# @cache.cached(timeout=timedelta(hours=3).seconds)
# def key(path: str):
#     return hls(path, 'key')


@app.route('/<string:path>.<string:extension>')
def hls(path: str, extension: str):
    # Add padding just in case
    url = urlsafe_b64decode(path + '====')

    response = hls_proxy(url, extension)
    return Response(response=response.body,
                    status=response.status,
                    headers=response.headers,
                    content_type=response.content_type)


if __name__ == '__main__':
    port = 8000

    server = pywsgi.WSGIServer(("localhost", port), app)
    server.serve_forever()
