import os
import re
from base64 import urlsafe_b64encode
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable
from urllib.parse import urljoin, urlparse
from consts import Extensions


@dataclass
class M3U8Tag:
    name: str
    attributes: dict[bytes, bytes]


class M3U8Parser:
    KEY_TAGS = [b'#EXT-X-KEY', b'#EXT-X-SESSION-KEY']
    ATTRIBUTELISTPATTERN = re.compile(rb"""((?:[^,"']|"[^"]*"|'[^']*')+)""")

    @classmethod
    def __remove_quotes(cls, string: bytes) -> bytes:
        quotes = (b'"', b"'")
        if string.startswith(quotes) and string.endswith(quotes):
            return string[1:-1]
        return string

    @classmethod
    def parse_tag_attributes(cls, line: bytes) -> M3U8Tag:
        tag, params = line.split(b':', maxsplit=1)
        params = cls.ATTRIBUTELISTPATTERN.split(params)[1::2]

        attributes = {}
        for param in params:
            name, value = param.split(b'=', maxsplit=1)
            attributes[name.decode()] = cls.__remove_quotes(value)

        return M3U8Tag(tag, attributes)


class M3U8Proxy:
    @classmethod
    @lru_cache
    def __proxy_tag_uri(cls, base: bytes, line: bytes) -> bytes:
        tag = M3U8Parser.parse_tag_attributes(line)

        uri = tag.attributes['URI']
        if not uri.startswith(b'http'):
            uri = urljoin(base, uri)

        if tag.name in M3U8Parser.KEY_TAGS:
            uri = urlsafe_b64encode(uri) + b'.key'
            # prefix = prefix.replace(Constant.HLS_ENDPOINT, Constant.KEY_ENDPOINT)

        return line.replace(tag.attributes['URI'], b'/' + uri)

    @classmethod
    def proxy_m3u8(cls, url: str, content: bytes) -> Iterable[bytes]:
        base_path = urljoin(url, '.').encode()

        for line in content.splitlines():
            if not line:
                # Empty line, just output as is
                yield line + b'\n'
            elif b'URI=' in line:
                yield cls.__proxy_tag_uri(base_path, line) + b'\n'
            elif line.startswith(b'#'):
                yield line + b'\n'
            else:
                if not line.startswith(b'http'):
                    line = urljoin(base_path, line)

                path = urlparse(line).path
                _, ext = os.path.splitext(path)
                # Ignore the dot
                if ext[1:] not in Extensions.get_all():
                    ext = b'.ts'
                yield b'/%b%b\n' % (urlsafe_b64encode(line), ext)
