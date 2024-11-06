import http.server
import socketserver


def run_callback_server(addr_: str, port_: int) -> None:
    """ Run a temporary server to serve as a callback URI for API that so require it.

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
