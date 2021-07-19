from json import JSONDecodeError
from typing import Any, Optional
import json as j

from werkzeug.wrappers import Request as _Request


class Request(_Request):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def set_current_user(self, user: Any) -> None:
        self.user = user

    @property
    def remote_port(self) -> str:
        return self.environ.get("REMOTE_PORT")

    @property
    def json(self) -> Optional[Any]:
        try:
            return j.loads(self.data)
        except JSONDecodeError:
            return None

    @property
    def is_websocket(self) -> bool:
        if self.headers.get("Connection") and self.headers.get("Upgrade") and self.headers.get(
                "Sec-WebSocket-Extensions") and self.headers.get("Sec-WebSocket-Key") and self.headers.get(
                "Sec-WebSocket-Version"):
            return True
        return False

    # @property
    # def origin(self) -> str:
    #     return self.headers.get('Origin', None)
