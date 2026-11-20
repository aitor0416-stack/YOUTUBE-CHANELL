#!/usr/bin/env python3
"""Servidor estático mínimo CON soporte de Range.

Por qué existe: <video> en Chromium necesita respuestas 206 (Range) para poder saltar a un segundo
concreto. El http.server normal de Python no las da y currentTime no se mueve, así que la revisión
con Playwright no sirve.

Uso: python3 servidor_rangos.py <carpeta> [puerto=8765]
Solo escucha en 127.0.0.1.
"""
import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class H(SimpleHTTPRequestHandler):
    def send_head(self):
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        a = int(m.group(1) or 0)
        b = min(int(m.group(2) or size - 1), size - 1)
        f = open(path, "rb")
        f.seek(a)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {a}-{b}/{size}")
        self.send_header("Content-Length", str(b - a + 1))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self._restante = b - a + 1
        return f

    def copyfile(self, src, dst):
        n = getattr(self, "_restante", None)
        if n is None:
            return super().copyfile(src, dst)
        while n > 0:
            buf = src.read(min(65536, n))
            if not buf:
                break
            dst.write(buf)
            n -= len(buf)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    os.chdir(sys.argv[1])
    puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
    ThreadingHTTPServer(("127.0.0.1", puerto), H).serve_forever()
