import gzip

import requests
from flask import Response, make_response

from modifier import proxied_m3u8
from pools import session


def chunked_read(response: requests.Response, chunk=64 * 1024, decode_content=None):
  for data in response.iter_content(chunk_size=None):
    if not data:
      break
    yield data

def handle_ts(url: bytes, root_url: bytes) -> Response:
  original_response = session.get(url=url.decode(), stream=True)
  body = chunked_read(original_response, decode_content=False)
  response = Response(response=body)
  response.content_type = original_response.headers.get('Content-Type', 'text/html; charset=utf-8')
  response.headers.add('content-encoding', original_response.headers.get('content-encoding', ''))
  response.headers.add('Access-Control-Allow-Origin', '*')
  return response

def handle_m3u8(url: bytes, root_url: bytes) -> Response:
  original_response = session.get(url=url.decode())
  body = gzip.compress(b'\n'.join(proxied_m3u8(url, original_response.content, root_url)))
  response = make_response(body, original_response.status_code)
  response.content_type = original_response.headers.get('Content-Type', 'text/html; charset=utf-8')
  response.headers.add('content-encoding', 'gzip')
  response.headers.add('Access-Control-Allow-Origin', '*')
  return response

def handle_key(url: bytes, root_url: bytes) -> Response:
  original_response = session.get(url=url.decode())
  body = original_response.content
  response = make_response(body, original_response.status_code)
  response.content_type = original_response.headers.get('Content-Type', 'text/html; charset=utf-8')
  response.headers.add('Access-Control-Allow-Origin', '*')
  return response

def handle_srt(url: bytes, root_url: bytes) -> Response:
  original_response = session.get(url=url.decode())
  body = original_response.content
  response = make_response(body, original_response.status_code)
  response.content_type = original_response.headers.get('Content-Type', 'text/html; charset=utf-8')
  response.headers.add('Access-Control-Allow-Origin', '*')
  return response

handlers = {
  '.ts': handle_ts,
  '.m3u8': handle_m3u8,
  '.srt': handle_srt,
  '.key': handle_key
}
