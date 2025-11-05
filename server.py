cat > server.py <<'PY'
#!/usr/bin/env python3
# server.py - tiny local fake DVNA server for demo (no npm needed)
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import html

HOST = "0.0.0.0"
PORT = 3000

# Seeded credentials for demo -> only these will succeed
SEED = {
    "alice@example.local": "secret123",
    # add more if you want: "bob@example.local": "BobPass1"
}

LOGIN_PAGE = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>DVNA - Simulated Login</title></head>
<body>
  <h2>Damn Vulnerable Node App (Simulated)</h2>
  <form method="post" action="/login">
    <label>Email:</label>
    <input type="text" name="username" /><br>
    <label>Password:</label>
    <input type="password" name="password" /><br>
    <input type="submit" value="Login" />
  </form>
  <p><i>Local demo only — no external connections.</i></p>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/login":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(LOGIN_PAGE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/login":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        data = parse_qs(body)
        user = data.get("username", [""])[0].strip()
        pwd = data.get("password", [""])[0]

        # simple check
        if user in SEED and SEED[user] == pwd:
            # success page
            content = f"""<html><body><h2>Welcome, {html.escape(user)}</h2>
                       <p>Dashboard</p>
                       </body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        else:
            # failure: return login page with message
            fail = LOGIN_PAGE.replace(
                "<form",
                "<p style='color:red'>Invalid username or password</p><form",
                1
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(fail.encode("utf-8"))

    def log_message(self, format, *args):
        # keep output concise
        print("%s - - %s" % (self.client_address[0], format%args))

if __name__ == "__main__":
    print(f"Serving fake DVNA on http://{HOST}:{PORT}  (CTRL+C to stop)")
    HTTPServer((HOST, PORT), Handler).serve_forever()
PY
