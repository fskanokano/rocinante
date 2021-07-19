import json
from functools import wraps
from typing import Callable

from .response import Response
from .request import Request


class ResponseWrapper(object):

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(endpoint, request: Request, **params) -> Response:
            response = func(endpoint, request, **params)
            if not isinstance(response, Response):
                response = self._process_response(response)
            return response

        return wrapper

    def _process_response(self, response) -> Response:
        if isinstance(response, tuple):
            if len(response) != 2:
                raise Exception("invalid response")
            data, status = response
            if isinstance(data, str):
                return Response(data, status)
            else:
                data = json.dumps(data)
                return Response(data, status, mimetype="application/json")
        elif isinstance(response, str):
            return Response(response)
        else:
            data = json.dumps(response)
            return Response(data, mimetype="application/json")


response_wrapper = ResponseWrapper()
