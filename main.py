import http.server
import socketserver
import urllib.request
import urllib.parse
import traceback

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        url = urllib.parse.parse_qs(query).get('url', [None])[0]

        if url:
            try:
                # Debug: print the requested URL
                print(f"Requesting URL: {url}")

                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    # Debug: print the response status and headers
                    print(f"Response Status: {response.status}")
                    print(f"Response Headers: {response.headers}")

                    self.send_response(response.status)

                    headers_to_remove = ['X-Frame-Options', 'Content-Security-Policy']
                    for header, value in response.headers.items():
                        if header not in headers_to_remove:
                            self.send_header(header, value)

                    self.end_headers()

                    # Debug: Print the first 100 bytes of the response
                    response_content = response.read()
                    print(f"Response Content (first 100 bytes): {response_content[:100]}")

                    self.wfile.write(response_content)
            except urllib.error.HTTPError as e:
                print(f"HTTP Error: {e.code} - {e.reason}")
                self.send_error(e.code, f"HTTP Error: {e.reason}")
            except urllib.error.URLError as e:
                print(f"URL Error: {e.reason}")
                self.send_error(500, f"URL Error: {e.reason}")
            except Exception as e:
                traceback.print_exc()
                self.send_error(500, f"Proxy error: {e}")
        else:
            self.send_error(400, "Bad Request: Missing URL parameter.")

PORT = 8000

with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
