import http.server
import socket
import socketserver
import subprocess
import re
import time


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
