import json
import os
from typing import Optional, Union, Mapping, Iterable, Tuple, BinaryIO

from werkzeug.wrappers import Response
from werkzeug.utils import send_file as _send_file
from jinja2 import Template

from .request import Request


class JSONResponse(Response):
    def __init__(
            self,
            response=None,
            status=None,
            headers=None,
            mimetype='application/json',
            content_type=None,
            direct_passthrough=False,
    ):
        response = json.dumps(response)
        super().__init__(
            response,
            status,
            headers,
            mimetype,
            content_type,
            direct_passthrough
        )


class NotFoundResponse(Response):
    def __init__(
            self,
            response='404 Not Found',
            status=404,
            headers=None,
            mimetype=None,
            content_type=None,
            direct_passthrough=False,
    ):
        super().__init__(
            response,
            status,
            headers,
            mimetype,
            content_type,
            direct_passthrough
        )


class ForbiddenResponse(Response):
    def __init__(
            self,
            response='403 Forbidden',
            status=403,
            headers=None,
            mimetype=None,
            content_type=None,
            direct_passthrough=False,
    ):
        super().__init__(
            response,
            status,
            headers,
            mimetype,
            content_type,
            direct_passthrough
        )


class MethodNotAllowedResponse(Response):
    def __init__(
            self,
            response='405 Method Not Allowed',
            status=405,
            headers=None,
            mimetype=None,
            content_type=None,
            direct_passthrough=False,
    ):
        super().__init__(
            response,
            status,
            headers,
            mimetype,
            content_type,
            direct_passthrough
        )


def render(
        template: str,
        status: Optional[int] = None,
        headers: Optional[
            Union[
                Mapping[str, Union[str, int, Iterable[Union[str, int]]]],
                Iterable[Tuple[str, Union[str, int]]],
            ]
        ] = None,
        mimetype: Optional[str] = "text/html",
        content_type: Optional[str] = None,
        direct_passthrough: bool = False,
        **context
):
    response = Template(open(template, encoding="utf-8").read()).render(**context)
    return Response(
        response,
        status,
        headers,
        mimetype,
        content_type,
        direct_passthrough
    )


def send_file(
        request: Request,
        path_or_file: Union[os.PathLike, str, BinaryIO],
        mimetype: Optional[str] = None,
):
    return _send_file(
        path_or_file=path_or_file,
        environ=request.environ,
        mimetype=mimetype
    )
