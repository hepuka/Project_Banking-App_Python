import http.server
import socketserver
import threading
import urllib.parse


class LoginServer:
    def __init__(self, bank, port=8080):
        self.bank = bank
        self.port = port
        self.httpd = None

        class Handler(http.server.SimpleHTTPRequestHandler):

            def do_GET(inner_self):
                inner_self.send_response(200)
                inner_self.send_header("Content-type", "text/html; charset=UTF-8")
                inner_self.end_headers()
                inner_self.wfile.write(
                    bank.HTML.format(error="").encode("utf-8")
                )

            def do_POST(inner_self):
                length = int(inner_self.headers.get('Content-Length'))
                body = inner_self.rfile.read(length).decode()
                post_data = urllib.parse.parse_qs(body)

                username = post_data.get("username", [""])[0]
                password = post_data.get("password", [""])[0]

                # 🔥 Itt a lényeg: már nem bank.users!
                if bank.login(username, password):

                    inner_self.send_response(200)
                    inner_self.send_header("Content-type", "text/html; charset=UTF-8")
                    inner_self.end_headers()

                    inner_self.wfile.write(
                        "<h3>Sikeres bejelentkezés</h3>"
                        "<script>setTimeout(() => window.close(), 1000);</script>"
                        .encode("utf-8")
                    )

                    # Szerver leállítása külön threadben
                    threading.Thread(target=bank.httpd.shutdown).start()
                    return

                # Hibás adatok
                inner_self.send_response(200)
                inner_self.send_header("Content-type", "text/html; charset=UTF-8")
                inner_self.end_headers()

                inner_self.wfile.write(
                    bank.HTML.format(
                        error="<p style='color:red'>Hibás felhasználónév vagy jelszó</p>"
                    ).encode("utf-8")
                )

        self.Handler = Handler

    def start(self):
        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(("", self.port), self.Handler)
        self.bank.httpd = self.httpd
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
