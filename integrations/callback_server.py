# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
Functions in this module are able to launch a basic web server
in case integrations use a callback URI that does not redirect to a browser instance.

Alternatively, this module can be utilised for fetching GET/POST requests coming from
integrations. Implemeted experimentally, only left if needed.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import http.server
import socketserver
import subprocess
import re


def callback_server_sub(addr_: str, port_: int, pattern: str) -> None:
    """Run a temporary server to serve as a callback URI for API that so require it.

    :param addr_: ``str`` address, typically ``localhost`` or ``127.0.0.47``
    :param port_: ``int`` port number, typically ``8888``
    :return: ``None`` (server will be activated until ``KeyboardInterrupt``)
    """
    server = subprocess.Popen(
        f"python3 -m http.server -b {addr_} {port_}",
        shell=True,
        text=True,
    )
    while True:
        stderr = server.stderr
        if re.findall(pattern, str(stderr)):
            server.kill()
            return stderr
        else:
            continue


def run_callback_server(addr_: str, port_: int) -> None:
    """Run a temporary server to serve as a callback URI for API that so require it.

    :param addr_: ``str`` address, typically ``localhost`` or ``127.0.0.47``
    :param port_: ``int`` port number, typically ``8888``
    :return: ``None`` (server will be activated until ``KeyboardInterrupt``)
    """
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer((addr_, port_), handler) as httpd:
        print("Listening at port", port_)
        httpd.serve_forever()
    return None


if __name__ == "__main__":
    run_callback_server("127.0.0.47", 8888)
