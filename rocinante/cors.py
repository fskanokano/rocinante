from typing import Sequence

from .middleware import Middleware
from .request import Request
from .response import Response

ALL_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]
SAFE_HEADERS = ["Accept", "Accept-Language", "Content-Language", "Content-Type"]


class CORSMiddleware(Middleware):

    def __init__(
            self,
            allow_origins: Sequence[str] = "*",
            allow_methods: Sequence[str] = "*",
            allow_headers: Sequence[str] = "*",
            allow_credentials: bool = False,
            expose_headers: Sequence[str] = "*",
            max_age: int = 600,
    ) -> None:
        simple_headers = {}

        preflight_headers = {}

        if allow_credentials:
            simple_headers["Access-Control-Allow-Credentials"] = "true"

        if expose_headers == "*":
            simple_headers["Access-Control-Expose-Headers"] = ", ".join(SAFE_HEADERS)
        else:
            simple_headers["Access-Control-Expose-Headers"] = ", ".join(allow_headers)

        if allow_headers == "*":
            preflight_headers["Access-Control-Allow-Headers"] = ", ".join(SAFE_HEADERS)
        else:
            preflight_headers["Access-Control-Allow-Headers"] = ", ".join(allow_headers)

        if allow_methods == "*":
            preflight_headers["Access-Control-Allow-Methods"] = ", ".join(ALL_METHODS)
        else:
            preflight_headers["Access-Control-Allow-Methods"] = ", ".join(allow_methods)

        preflight_headers["Access-Control-Max-Age"] = str(max_age)

        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers
        self.max_age = max_age

        self.simple_headers = simple_headers

        self.preflight_headers = preflight_headers

    def before_request(self, request: Request, **params):
        if request.is_websocket:
            return

        origin = request.origin

        if origin is not None:

            if self.allow_origins != "*":
                if origin not in self.allow_origins:
                    return Response(status=403)

            if request.method == "OPTIONS":
                simple_headers = self._process_origin(origin)
                return self._preflight_response(simple_headers)

    def after_response(self, request: Request, response: Response, **params):
        if request.is_websocket:
            return

        origin = request.origin

        if origin is not None:
            simple_headers = self._process_origin(origin)
            for key, value in simple_headers.items():
                response.headers.add_header(key, value)

    def _preflight_response(self, simple_headers: dict) -> Response:
        simple_headers.update(self.preflight_headers)
        return Response(
            status=204,
            headers=simple_headers
        )

    def _process_origin(self, origin: str) -> dict:
        simple_headers = self.simple_headers.copy()
        if self.allow_origins == "*":
            if self.allow_credentials:
                simple_headers["Access-Control-Allow-Origin"] = origin
            else:
                simple_headers["Access-Control-Allow-Origin"] = "*"
        else:
            simple_headers["Access-Control-Allow-Origin"] = origin
        return simple_headers
