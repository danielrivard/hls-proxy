from typing import Iterable, Tuple

from pybase64 import b64encode

from consts import Constant
from hooks import resource_replace


def is_key_line(line: bytes) -> bool:  
  return line.startswith(Constant.EXT_KEY)

def extract_key(line: bytes) -> Tuple[int, int]:
  apos = b'"'
  start = line.find(apos, len(Constant.EXT_KEY)) + 1
  end = line.find(apos, start)
  return (start, end)

def proxied_key_line(base: bytes, line: bytes, root_url: bytes) -> bytes:
  start, end = extract_key(line)
  key = line[start:end]
  if not key.startswith(b'http'):
    key = base + key
  proxied_key = resource_replace(key, '')
  b64_key = b64encode(proxied_key)
  proxied_key = b'%b%b.key' % (root_url, b64_key)
  return line[:start] + proxied_key + line[end:]

def proxied_m3u8(url: bytes, text: bytes, root_url = None) -> Iterable[bytes]:
  base = url[:url.rfind(b'/') + 1]
  
  for line in text.splitlines():
    if is_key_line(line):
      yield proxied_key_line(base, line, root_url)
    elif line.startswith(b'#'):
      yield line
    else:
      line = resource_replace(line)
      if not line.startswith(b'http') and line:
        line = base + line
      if line:
        ext = line[line.rfind(b'.'):]
        b64 = b64encode(line)
        yield b'%b%b%b' % (root_url, b64, ext)
      else:
        yield line