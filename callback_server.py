import http.server
import socketserver


def run_callback_server(addr_, port_) -> None:
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer((addr_, port_), handler) as httpd:
        print("Listening at port", port_)
        httpd.serve_forever()
    return None


run_callback_server("127.0.0.47", 8888)
