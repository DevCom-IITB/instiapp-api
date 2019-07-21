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
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

def send_302(obj, loc):
    obj.send_response(302)
    obj.send_header('Location', loc)
    obj.end_headers()

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if 'PROFILE' in self.path:
            self._set_headers()
            auth = str(self.headers["Authorization"])
            if "Bearer ACCESS_TOKEN" in auth:
                data = {
                    "id": 3,
                    "username": "username",
                    "first_name": "FIRST NAME",
                    "type": "TYPE",
                    "profile_picture": "/sso/path/to/profile_picture_file",
                    "last_name": "Last name",
                    "sex": "SEX",
                    "email": "username@iitb.ac.in",
                    "mobile": "0123456789",
                    "roll_number": "123456789",
                    "program": {
                        "id": 1,
                        "department": "DEPARTMENT",
                        "department_name": "FULL_DEPARTMENT_NAME",
                        "join_year": 2012,
                        "graduation_year": 2016,
                        "degree": "DEGREE",
                        "degree_name": "FULL_DEGREE_NAME"
                    },
                    "secondary_emails": [
                        {"id": 1, "email": "user_email@gmail.com"}
                    ],
                    "contacts": [
                        {"id": 1, "number": "9876543210"}
                    ],
                    "insti_address": {
                        "id": 1,
                        "room": "room_number",
                        "hostel": "HOSTEL",
                        "hostel_name": "FULL_HOSTEL_NAME"
                    }
                }
                self.wfile.write(json.dumps(data).encode())
            elif "Bearer LOW_PRIV_ACCESS_TOKEN" in auth:
                self.wfile.write(b'{"id":3,"username":"username"}')
            else:
                self.wfile.write(b'{"error":"wrong access token"}')
        elif 'SSO' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Set-Cookie', 'csrftoken=BIGCSRF')
            self.end_headers()
            self.wfile.write(b'Random HTML')

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        # print("URL --> " + self.path)
        # print(str(post_data))

        token_url = "CODE_TOKEN"
        bad_token_test = "code=BAD_TEST_CODE"
        token_test = "code=TEST_CODE&redirect_uri=REDIRECT_URI&grant_type=authorization_code"
        token_test_lp = "code=TEST_CODE_LP&redirect_uri=REDIRECT_URI&grant_type=authorization_code"

        USERNAME = "biguser"
        PASSWORD = "bigpass"
        FUSERNAME = "smalluser"
        FPASSWORD = "smallpass"

        if token_url in self.path:
            self._set_headers()
            if bad_token_test in str(post_data):
                self.wfile.write(b'{"access_token":"BAD_ACCESS_TOKEN"}')
            elif token_test in str(post_data):
                self.wfile.write(b'{"access_token":"ACCESS_TOKEN"}')
            elif token_test_lp in str(post_data):
                self.wfile.write(b'{"access_token":"LOW_PRIV_ACCESS_TOKEN"}')
            else:
                self.wfile.write(b'{"error":"auth test failed"}')

        elif "/SSOAUTH" in self.path:
            send_302(self, 'http://localhost:33000/SSOREDIR/?code=TEST_CODE')

        elif "/SSO" in self.path:
            if USERNAME in str(post_data) and PASSWORD in str(post_data):
                send_302(self, 'http://localhost:33000/SSOREDIR/?code=TEST_CODE')
            elif FUSERNAME in str(post_data) and FPASSWORD in str(post_data):
                send_302(self, 'http://localhost:33000/SSOAUTH/')
            else:
                self._set_headers()
                self.wfile.write(b'{"error":"auth test failed"}')

    def log_message(self, format, *args):  # pylint: disable=W0622
        return

def run(server_class=HTTPServer, handler_class=S, port=33000):
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    # print('Starting httpd...')
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
