from typing import Optional, List, Type

from geventwebsocket import WebSocketError
from geventwebsocket.websocket import WebSocket

from .request import Request
from .response import MethodNotAllowedResponse, Response, ForbiddenResponse
from .middleware import Middleware
from .wrapper import response_wrapper


class HTTPEndpoint(object):
    exempted_middlewares: List[Type[Middleware]] = []

    @response_wrapper
    def dispatch(self, request: Request, **params) -> Response:
        method = request.method
        handler = getattr(self, method.lower(), None)
        if handler is None:
            return MethodNotAllowedResponse()
        return handler(request, **params)

    def options(self, request: Request, **params):
        return Response(status=204)


class WebSocketEndpoint(HTTPEndpoint):
    def __init__(self):
        self.ws: Optional[WebSocket] = None

    def _initialize(self, ws: WebSocket) -> None:
        self.ws = ws

    def dispatch(self, request: Request, **params) -> Response:
        ws: WebSocket = request.environ.get('wsgi.websocket', None)
        if ws is None:
            return ForbiddenResponse()

        if not self.accept(request, **params):
            ws.close()
            return ForbiddenResponse()

        self._initialize(ws)
        self.on_open()
        while True:
            try:
                message = ws.receive()
                if message is not None:
                    self.on_message(message)
            except WebSocketError:
                self.on_close()
                break
        return Response()

    def accept(self, request: Request, **params) -> bool:
        return True

    def on_open(self):
        pass

    def on_message(self, message: str):
        pass

    def on_close(self):
        pass
