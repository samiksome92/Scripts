#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# ///

"""A script implementing a simple http server with custom `Cache-Control` headers."""

import argparse
import http.server
import sys


class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Request handler for no cache server.

    Extends `SimpleHTTPRequestHandler` and adds `no-cache` `Cache-Control` headers to responses.
    """

    def send_response_only(self, code: int, message: str | None = None) -> None:
        """Sends response with `no-cache` `Cache-Control` headers.

        Parameters
        ----------
        code : int
            Response code.
        message : str | None
            Response message. (default=`None`)
        """
        super().send_response_only(code, message=message)
        self.send_header("Cache-Control", "no-cache")


def main() -> None:
    """Parses arguments and runs the server."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Port to use", type=int, default=8000)
    args = parser.parse_args()

    NoCacheHTTPRequestHandler.protocol_version = "HTTP/1.1"
    with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), NoCacheHTTPRequestHandler) as httpd:
        print(f"Serving HTTP on 127.0.0.1 port {args.port} (http://127.0.0.1:{args.port}/) ...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)


if __name__ == "__main__":
    main()
