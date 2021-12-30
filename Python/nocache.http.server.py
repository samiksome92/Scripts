#!/usr/bin/env python3

"""A script implementing a simple http server with custom cache control headers."""

import http.server
from typing import Union


class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Request handler for no cache server.

    Extends SimpleHTTPRequestHandler and adds no-cache and must-revalidate Cache-Control headers to responses.
    """

    def send_response_only(self, code: int, message: Union[str, None] = None) -> None:
        """Add Cache-Control headers and Expires header."""
        super().send_response_only(code, message=message)
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Expires', '0')


def main() -> None:
    """Main function for script. Tests the NoCacheHTTPRequestHandler class."""
    http.server.test(HandlerClass=NoCacheHTTPRequestHandler, bind="127.0.0.1", port=8000)


if __name__ == '__main__':
    main()
