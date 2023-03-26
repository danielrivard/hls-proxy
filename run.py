import logging

from flask import Flask, make_response, request
from gevent import pywsgi

logging.basicConfig(level=logging.DEBUG)

from pybase64 import b64decode

from consts import Constant
from handlers import handlers

app = Flask(__name__)

@app.route('/<string:path>')
def on_request(path: str):
  root_url = request.root_url.encode()

  for ext in Constant.EXTS:
    if ext in path:
      payload = path[:-len(ext)] + '==='
      url = b64decode(payload.encode())

      return handlers[ext](url, root_url)
  else:
    return make_response('NG', 400)


if __name__ == '__main__':
  port = 8000
  
  server = pywsgi.WSGIServer(("localhost", port), app)
  server.serve_forever()