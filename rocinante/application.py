import sys
from typing import Iterable, List, Optional, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from _typeshed.wsgi import WSGIEnvironment
    from _typeshed.wsgi import StartResponse

from gevent.pywsgi import WSGIServer
from werkzeug import run_simple
from werkzeug.routing import Map
from werkzeug.exceptions import NotFound
from loguru import logger

from .blueprint import Blueprint
from .route import Route, Static
from .response import NotFoundResponse
from .request import Request
from .endpoint import HTTPEndpoint
from .middleware import Middleware
from .handler import BaseHandler


class Rocinante(object):
    url_map = Map()

    def __init__(
            self,
            *,
            routes: Optional[List[Route]] = None,
            middlewares: Optional[List[Middleware]] = None,
            blueprints: Optional[List["Blueprint"]] = None,
            statics: Optional[List[Static]] = None
    ):
        if routes is not None:
            for route in routes:
                route.register_route(self, middlewares)

        if middlewares is None:
            self.middlewares = []
        else:
            self.middlewares = middlewares

        if blueprints is None:
            self.blueprints = []
        else:
            self.blueprints = blueprints
            self._register_blueprints()

        if statics is not None:
            self.statics = statics
            for static in statics:
                static.register_static_route(self)
        else:
            self.statics = []

    def __call__(self, environ: "WSGIEnvironment", start_response: "StartResponse") -> Iterable[bytes]:
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ: "WSGIEnvironment", start_response: "StartResponse") -> Iterable[bytes]:
        adapter = self.url_map.bind_to_environ(environ)
        try:
            endpoint, params = adapter.match()
            endpoint_instance: HTTPEndpoint = endpoint()
            params: dict
            request = Request(environ)
            response = endpoint_instance.dispatch(request, **params)
            return response(environ, start_response)
        except NotFound:
            return NotFoundResponse()(environ, start_response)

    def _register_blueprints(self):
        for blueprint in self.blueprints:
            self._initial_blueprint(blueprint)

    def _initial_blueprint(self, blueprint: Blueprint):
        middlewares, prefix = self._build_middlewares_and_prefix(blueprint)
        for route in blueprint.routes:
            route.register_route(self, middlewares, prefix)
        for blueprint_ in blueprint.blueprints:
            self._initial_blueprint(blueprint_)

    def _build_middlewares_and_prefix(self, blueprint: Blueprint) -> Tuple[List[Middleware], str]:
        middlewares = []
        prefix = ""
        while blueprint is not None:
            middlewares = blueprint.middlewares + middlewares
            prefix = blueprint.prefix + prefix
            blueprint = blueprint.parent
        middlewares = self.middlewares + middlewares
        return middlewares, prefix

    def run_simple(self, host: str = '0.0.0.0', port: int = 8000, *, debug: bool = True) -> None:
        run_simple(host, port, self, use_debugger=debug, use_reloader=debug)

    def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        self._init_logger()
        self._log_startup(host, port)
        self._log_routes()

        server = WSGIServer(
            listener=(host, port),
            application=self,
            handler_class=BaseHandler
        )
        server.serve_forever()

    def _init_logger(self):
        logger.remove()
        logger.add(
            sys.stdout,
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <red>|</red> <level>{level}</level> <red>|</red> <level>{message}</level>"
        )

    def _log_startup(self, host: str, port: int) -> None:
        logger.debug("* Running on gevent server.")
        logger.warning("* This is a development server. Do not use it in a production deployment.")
        logger.debug(f"* Running on http://{host}:{port}/ (Press CTRL+C to quit)\n")

    def _log_routes(self) -> None:
        for rule in self.url_map._rules:
            if not rule.websocket:
                logger.debug(f'HTTP  "{rule.rule}"  -->  {rule.endpoint}')
            else:
                logger.debug(f'WebSocket  "{rule.rule}"  -->  {rule.endpoint}')
        for static in self.statics:
            if self.statics.index(static) == len(self.statics) - 1:
                logger.debug(f'Static  "{static.prefix}/*"  -->  {static.static_folder_full_path}\n')
            else:
                logger.debug(f'Static  "{static.prefix}/*"  -->  {static.static_folder_full_path}')
