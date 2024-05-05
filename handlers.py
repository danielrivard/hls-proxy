from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Iterable

from requests import Response

from consts import Extensions
from modifier import M3U8Proxy


@dataclass
class ProxyResponse:
    body: Iterable[bytes] | bytes | Iterable[str] | str | None = None
    status: int | HTTPStatus | None = None
    headers: dict[str, str] = field(default_factory=lambda: {})
    content_type: str | None = None


class ProxyHandler(ABC):
    def __init__(self) -> None:
        self._to_proxy = None

    @property
    @abstractmethod
    def _content_type(self) -> str:
        pass

    @property
    def _body(self) -> Iterable[bytes] | bytes | Iterable[str] | str | None:
        return self._to_proxy.content

    def handle(self, to_proxy: Response) -> ProxyResponse:
        self._to_proxy = to_proxy

        response = ProxyResponse(body=self._body,
                                 status=self._to_proxy.status_code,
                                 headers={'Access-Control-Allow-Origin': '*'},
                                 content_type=self._content_type)
        return response


class SegmentHandler(ProxyHandler):
    @property
    def _content_type(self) -> str:
        return 'video/MP2T'

    @property
    def _body(self) -> Iterable[bytes]:
        chunk = 64 * 1024
        for data in self._to_proxy.iter_content(chunk_size=chunk, decode_unicode=False):
            if not data:
                break
            yield data


class PlaylistHandler(ProxyHandler):
    @property
    def _content_type(self) -> str:
        return 'application/x-mpegURL'

    @property
    def _body(self) -> Iterable[bytes] | bytes | Iterable[str] | str | None:
        return M3U8Proxy.proxy_m3u8(self._to_proxy.url, self._to_proxy.content)


class KeyHandler(ProxyHandler):
    @property
    def _content_type(self) -> str:
        return 'application/octet-stream'


class SubtitlesHandler(ProxyHandler):
    @property
    def _content_type(self) -> str:
        return 'application/x-subrip'


class ProxyHandlerFactory:
    __handlers: dict[str, ProxyHandler] = None

    @classmethod
    def __get_handlers(cls):
        # Create a map of extension -> handler
        if cls.__handlers is None:
            cls.__handlers = {
                Extensions.PLAYLIST: PlaylistHandler(),
                Extensions.SEGMENT: SegmentHandler(),
                Extensions.KEY: KeyHandler(),
                Extensions.SUBTITLES: SubtitlesHandler()
            }
        return cls.__handlers

    @classmethod
    def get_handler(cls, extension: str) -> ProxyHandler:
        return cls.__get_handlers().get(extension, None)
