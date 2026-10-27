#!/usr/bin/env python3
"""Start the built public site from any directory and open it in a browser."""
from pathlib import Path
import http.server,functools,socketserver,webbrowser
ROOT=Path(__file__).resolve().parent
if not (ROOT/'site/index.html').is_file():raise SystemExit('Missing site/index.html; extract complete development ZIP.')
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT/'site'))
class Reusable(socketserver.TCPServer):allow_reuse_address=True
try:server=Reusable(('127.0.0.1',8000),handler)
except OSError:server=Reusable(('127.0.0.1',0),handler)
with server:
    url=f'http://127.0.0.1:{server.server_address[1]}/'
    print('The Jam Archive public preview: '+url+'\nPress Control+C to stop.')
    webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
