"""Serve o laboratório na própria máquina e recebe somente a figura incluída."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PASTA = Path(__file__).resolve().parent
FIGURA = (PASTA / "imagem-teste.png").read_bytes()
RECEBIDA = PASTA / "imagem-teste-recebida.png"
HOST = "127.0.0.1"
PORTA = 8000


class Laboratorio(BaseHTTPRequestHandler):
    def responder(self, status, tipo, dados):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        if self.path == "/":
            self.responder(200, "text/html; charset=utf-8", (PASTA / "index.html").read_bytes())
        elif self.path == "/imagem-teste.png":
            self.responder(200, "image/png", FIGURA)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/imagem-teste":
            self.send_error(404)
            return

        if self.headers.get("Origin") != f"http://{HOST}:{self.server.server_port}":
            self.send_error(403)
            return

        if self.headers.get_content_type() != "image/png":
            self.send_error(415)
            return

        if self.headers.get("Content-Length") != str(len(FIGURA)):
            self.send_error(400, "Tamanho diferente da figura de teste")
            return

        if self.rfile.read(len(FIGURA)) != FIGURA:
            self.send_error(400, "Somente a figura de teste e aceita")
            return

        try:
            RECEBIDA.write_bytes(FIGURA)
        except OSError:
            self.send_error(500, "Nao foi possivel salvar a figura de teste")
            return

        comprovante = {"arquivo": RECEBIDA.name, "bytes": len(FIGURA)}
        self.responder(200, "application/json", json.dumps(comprovante).encode("utf-8"))


if __name__ == "__main__":
    with HTTPServer((HOST, PORTA), Laboratorio) as servidor:
        print(f"Abra http://{HOST}:{PORTA}/ (Ctrl+C para encerrar)", flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass
