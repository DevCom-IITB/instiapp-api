"""Test server for News Chore"""
from http.server import BaseHTTPRequestHandler, HTTPServer

placement_2 = False

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/xml')
        self.end_headers()

    def do_GET(self):
        global placement_2  # pylint: disable=global-statement

        p = self.path.lower()

        # Choose the right feed
        file = None
        if 'body1blog' in p:
            file = 'sample-feed-1.xml'
        elif 'body2blog' in p:
            file = 'sample-feed-2.xml'
        elif 'body3blog' in p:
            file = 'sample-feed-3.xml'

        # PT blogs
        elif 'placementblog' in p:
            if not placement_2:
                file = 'sample-feed-p.xml'
                placement_2 = True
            else:
                file = 'sample-feed-p2.xml'
        elif 'trainingblog' in p:
            file = 'sample-feed-t.xml'

        # File not found
        if not file:
            self.send_response(404)
            self.end_headers()
            return

        # Set headers and write
        self.do_HEAD()
        with open('news/test/' + file, 'rb') as f:
            self.wfile.write(f.read())

    def do_HEAD(self):
        self._set_headers()

    def log_message(self, format, *args):  # pylint: disable=W0622
        return

def run(server_class=HTTPServer, handler_class=S, port=33000):
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
