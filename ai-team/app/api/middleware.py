"""
Attaches a request id to every request.

Raw ASGI rather than BaseHTTPMiddleware: contextvars survive, and we skip
its overhead and streaming edge cases.
"""

from app.common.context import new_request_id, set_request_id


class RequestIdMiddleware:
    HEADER = b"x-request-id"

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = dict(scope.get("headers") or {}).get(self.HEADER)
        request_id = incoming.decode() if incoming else new_request_id()
        set_request_id(request_id)
        scope.setdefault("state", {})["request_id"] = request_id

        async def send_with_header(message):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.append((self.HEADER, request_id.encode()))
            await send(message)

        await self.app(scope, receive, send_with_header)
