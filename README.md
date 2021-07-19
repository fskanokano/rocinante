## Rocinante

#### rocinante is a lightweight web application framework written by werkzeug.

## ⚙️ Installation

```bash
$ pip install rocinante

```

## ⚡️ Quickstart

```python
from rocinante import Rocinante, HTTPEndpoint, Route, Request


class HelloWorld(HTTPEndpoint):

    def get(self, request: Request):
        return "hello world"


routes = [
    Route("/", HelloWorld)
]

app = Rocinante(
    routes=routes
)

if __name__ == '__main__':
    app.run()
```

## 👀 Examples

Some common examples are listed below.

#### 📖 Basic Routing

```python
from rocinante import Rocinante, Request, Route, HTTPEndpoint


class Foo(HTTPEndpoint):

    def get(self, request: Request, foo_id: str):
        # return a json response and set status code
        return {
                   "method": request.method,
                   "foo_id": foo_id
               }, 200

    def post(self, request: Request, foo_id: str):
        return {
                   "method": request.method,
                   "foo_id": foo_id
               }, 201


routes = [
    Route("/foo/<foo_id>", Foo)
]

app = Rocinante(
    routes=routes
)

if __name__ == '__main__':
    app.run()
```

#### 📖 Render Template

```python
from rocinante import Request, HTTPEndpoint, render


class Foo(HTTPEndpoint):

    def get(self, request: Request, foo_id: str):
        return render(
            "test.html",
            foo_id=foo_id
        )
```

#### 📖 Send File

```python
from rocinante import Request, HTTPEndpoint, send_file


class Sender(HTTPEndpoint):

    def get(self, request: Request):
        return send_file(
            request,
            "test.txt"
        )
```

#### 📖 Middleware

```python
from rocinante import Rocinante, HTTPEndpoint, Middleware, Request, Response, JSONResponse, Route


class FooMiddleware(Middleware):

    def before_request(self, request: Request, **params):
        foo_id = params["foo_id"]
        if foo_id != 1:
            # return a json response to interrupt this request.
            return JSONResponse(
                {
                    "error": "foo_id is not 1"
                },
                401
            )
        print("before foo")

    def after_response(self, request: Request, response: Response, **params):
        foo_id = params["foo_id"]
        if foo_id != 1:
            # add a response header to this response.
            response.headers.add_header("Foo-Id", foo_id)
        print("after foo")


class Foo(HTTPEndpoint):

    def get(self, request: Request, foo_id: str):
        return "foo"


class ExemptedFoo(HTTPEndpoint):
    # configure the middlewares to be exempted
    exempted_middlewares = [FooMiddleware]

    def get(self, request: Request):
        return "exempted foo"


app = Rocinante(
    routes=[
        Route("/foo/<foo_id>", Foo)
    ],
    middlewares=[
        FooMiddleware(),
    ]
)
```

#### 📖 WebSocket

```python
from rocinante import Rocinante, WebSocketEndpoint, WebSocketRoute


class TestWebSocketEndpoint(WebSocketEndpoint):

    def on_open(self):
        print("opened")

    def on_message(self, message: str):
        print(f"received message:{message}")
        self.ws.send(message)

    def on_close(self):
        print("closed")


app = Rocinante(
    routes=[
        WebSocketRoute("/test", TestWebSocketEndpoint)
    ]
)
```

#### 📖 Serving Static File

```python
from rocinante import Rocinante, Static

app = Rocinante(
    statics=[
        Static("/file", __file__, "files"),
        Static("/image", __file__, "images")
    ]
)
```

#### 📖 Blueprint

The usage of blueprint is the same as rocinante application, only need to be registered to rocinante application, and
blueprint support infinite nesting (registering another sub-blueprint in one blueprint).

```python
from rocinante import Rocinante, Blueprint, HTTPEndpoint, Route, Request


class Foo(HTTPEndpoint):

    def get(self, request: Request, foo_id: str):
        return "blueprint foo"


foo_blueprint = Blueprint(
    prefix="/foo",
    routes=[
        Route("/<foo_id>", Foo)
    ]
)

app = Rocinante(
    blueprints=[
        foo_blueprint
    ]
)
```

#### 📖 CORS

rocinante provides a simple CORS middleware.

```python
from rocinante import Rocinante
from rocinante.cors import CORSMiddleware

app = Rocinante(
    middlewares=[
        CORSMiddleware(
            allow_origins=["www.example.com"],
            allow_methods=["GET", "POST", "DELETE", "PUT"],
            allow_headers=["Custom-Header"],
            allow_credentials=True,
            expose_headers=["Exposed-Header"],
            max_age=3600
        )
    ]
)
```
