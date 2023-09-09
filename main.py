from threading import Thread
from time import sleep
from datetime import datetime
from http import client
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import socket
import threading
import json


def sock_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))

        try:
            while True:
                data = s.recv(1024)
                if not data:
                    break
                received_message = json.loads(data.decode("utf-8"))

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

                try:
                    with open("storage/data.json", "r") as json_file:
                        data = json.load(json_file)
                except FileNotFoundError:
                    data = {}

                data[current_time] = received_message

                with open("storage/data.json", "w") as json_file:
                    json.dump(data, json_file, indent=2)

        except KeyboardInterrupt:
            print(f"Destroy server")


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "message.html":
            self.send_html_file("message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        print(data_dict)

        data_str = json.dumps(data_dict)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock_address = ("localhost", 5000)
            sock.connect(sock_address)
            message = data_str
            sock.sendall(message.encode())

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 5000

    socket_server = threading.Thread(target=sock_server, args=(HOST, PORT))
    http_server = threading.Thread(target=run, args=())

    socket_server.start()
    http_server.start()
