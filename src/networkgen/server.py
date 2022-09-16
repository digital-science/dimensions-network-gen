import http.server
import os
import socketserver

from ..settings import *

def go(port):
    web_dir = DEFAULT_BUILD_PATH
    os.chdir(web_dir)
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"\n\n-------\nServing at http://127.0.0.1:{port} ...")
        httpd.serve_forever()
