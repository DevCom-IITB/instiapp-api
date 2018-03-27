"""
Very simple HTTP server in python.
Usage::
    ./dummy-web-server.py [<port>]
Send a GET request::
    curl http://localhost
Send a HEAD request::
    curl -I http://localhost
Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost
"""
from http.server import BaseHTTPRequestHandler, HTTPServer

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        auth = str(self.headers["Authorization"])
        if "Bearer ACCESS_TOKEN" in auth:
            self.wfile.write(b'{"id":1,"username":"username","first_name":"First Name","type":"TYPE","profile_picture":"/sso/path/to/profile_picture_file","last_name":"Last Name","sex":"SEX","email":"username@iitb.ac.in","mobile":"0123456789","roll_number":"123456789","program":{"id":1,"department":"DEPARTMENT","department_name":"FULL_DEPARTMENT_NAME","join_year":2012,"graduation_year":2016,"degree":"DEGREE","degree_name":"FULL_DEGREE_NAME"},"secondary_emails":[{"id":1,"email":"user_email@gmail.com"}],"contacts":[{"id":1,"number":"9876543210"}],"insti_address":{"id":1,"room":"room_number","hostel":"HOSTEL","hostel_name":"FULL_HOSTEL_NAME"}}')
        else:
            self.wfile.write(b'{"error":"wrong access token"}')

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        print("URL --> " + self.path)
        print(str(post_data))
        self._set_headers()

        token_url = "CODE_TOKEN"
        token_test = "code=TEST_CODE&redirect_uri=REDIRECT_URI&grant_type=authorization_code"
        if token_url in self.path and token_test in str(post_data):
            self.wfile.write(b'{"access_token":"ACCESS_TOKEN"}')
        else:
            self.wfile.write(b'{"error":"auth test failed"}')

def run(server_class=HTTPServer, handler_class=S, port=33000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
