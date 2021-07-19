from typing import Optional, Callable
from functools import wraps

from .request import Request
from .response import Response


class Middleware(object):

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(endpoint, request: Request, **params) -> Optional[Response]:
            before_request_response = self.before_request(request, **params)
            if before_request_response is not None:
                return before_request_response

            response = func(endpoint, request, **params)

            self.after_response(request, response, **params)
            return response

        return wrapper

    def before_request(self, request: Request, **params):
        pass

    def after_response(self, request: Request, response: Response, **params):
        pass
