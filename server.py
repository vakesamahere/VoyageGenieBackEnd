import http.server
import socketserver
import time,json
from ChatAgent import AgentChat

class StreamHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        #stream
        self.send_response(200)
        self.send_header('Transfer-Encoding', 'chunked')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Credentials','true')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        for i in range(10):
            json_string = json.dumps({"id":str(i+1),"cost":"1"})
            self.wfile.write(json_string.encode('utf-8'))
            self.wfile.flush()
            print(json_string)
            time.sleep(1)
    def do_POST(self):
        pass

if __name__ == "__main__":
    PORT = 8000
    with socketserver.TCPServer(("", PORT), StreamHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()
