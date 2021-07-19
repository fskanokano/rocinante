import os
from typing import List, Type, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed.wsgi import WSGIApplication

from werkzeug.routing import Rule
from werkzeug.middleware.shared_data import SharedDataMiddleware

from .endpoint import HTTPEndpoint
from .middleware import Middleware


class Route(object):

    def __init__(
            self,
            rule: str,
            endpoint: Type[HTTPEndpoint]
    ):
        self.rule = rule
        self.endpoint = endpoint

    def register_route(self, app, middlewares: Optional[List[Middleware]], prefix: Optional[str] = None):
        self._build_middleware_stack(middlewares)
        if prefix is not None:
            app.url_map.add(Rule(prefix + self.rule, endpoint=self.endpoint))
        else:
            app.url_map.add(Rule(self.rule, endpoint=self.endpoint))

    def _build_middleware_stack(self, middlewares: Optional[List[Middleware]]) -> None:
        if middlewares is not None:
            for middleware in reversed(middlewares):
                if middleware.__class__ not in self.endpoint.exempted_middlewares:
                    self.endpoint.dispatch = middleware(self.endpoint.dispatch)


class WebSocketRoute(Route):

    def register_route(self, app, middlewares: Optional[List[Middleware]], prefix: Optional[str] = None):
        self._build_middleware_stack(middlewares)
        if prefix is not None:
            app.url_map.add(Rule(prefix + self.rule, endpoint=self.endpoint, websocket=True))
        else:
            app.url_map.add(Rule(self.rule, endpoint=self.endpoint, websocket=True))


class Static(object):

    def __init__(
            self,
            prefix: str,
            root: str,
            static_folder: str
    ):
        self.prefix = prefix
        self.static_folder_full_path = os.path.join(os.path.dirname(root), static_folder)

    def register_static_route(self, app: "WSGIApplication"):
        app.wsgi_app = SharedDataMiddleware(
            app.wsgi_app,
            {
                self.prefix: self.static_folder_full_path
            }
        )
