from http import HTTPStatus

from handlers import ProxyHandlerFactory, ProxyResponse
from http_helpers import http_client


def hls_proxy(url: bytes, extension: str) -> ProxyResponse:
    response_to_proxy = http_client.get(url=url,
                                        stream=True,
                                        allow_redirects=False,
                                        timeout=3)

    if not response_to_proxy.ok:
        return ProxyResponse(body=response_to_proxy.content, status=response_to_proxy.status_code)

    if response_to_proxy.is_redirect:
        response_to_proxy = http_client.get(response_to_proxy.headers['location'], stream=True, timeout=3)

    if (handler := ProxyHandlerFactory.get_handler(extension)):
        return handler.handle(response_to_proxy)

    return ProxyResponse(body=f'Bad Request, Unsupported Extension: {extension}',
                         status=HTTPStatus.BAD_REQUEST)
