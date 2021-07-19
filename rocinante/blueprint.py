from typing import List, Optional, Type

from .route import Route
from .middleware import Middleware


class Blueprint(object):

    def __init__(
            self,
            *,
            prefix: str,
            routes: Optional[List[Route]] = None,
            middlewares: Optional[List[Middleware]] = None,
            blueprints: Optional[List["Blueprint"]] = None
    ):
        self.prefix = prefix

        if routes is None:
            self.routes = []
        else:
            self.routes = routes

        if middlewares is None:
            self.middlewares = []
        else:
            self.middlewares = middlewares

        if blueprints is None:
            self.blueprints = []
        else:
            self.blueprints = blueprints
            self._register_blueprints()

        self.parent: Optional["Blueprint"] = None

    def _register_blueprints(self):
        for blueprint in self.blueprints:
            blueprint.parent = self
