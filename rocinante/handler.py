from geventwebsocket.handler import WebSocketHandler
from loguru import logger


class BaseHandler(WebSocketHandler):

    def log_request(self):
        status = int((self._orig_status or self.status or '000').split()[0])
        if status < 400:
            logger.info(self.format_request())
        else:
            logger.error(self.format_request())

    def format_request(self):
        if self.time_finish:
            delta = '%.6f' % (self.time_finish - self.time_start)
        else:
            delta = '-'
        client_address = self.client_address[0] if isinstance(self.client_address, tuple) else self.client_address
        requestline = self.requestline
        if self.environ.get("HTTP_CONNECTION") and self.environ.get("HTTP_UPGRADE") and self.environ.get(
                "HTTP_SEC_WEBSOCKET_VERSION") and self.environ.get("HTTP_SEC_WEBSOCKET_KEY") and self.environ.get(
            "HTTP_SEC_WEBSOCKET_EXTENSIONS"):
            requestline = requestline.replace("GET", "WebSocket")
        return '%s - - "%s" %s %s' % (
            client_address or '-',
            requestline or '',
            (self._orig_status or self.status or '000').split()[0],
            delta)
