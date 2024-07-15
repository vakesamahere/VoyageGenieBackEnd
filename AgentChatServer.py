import http.server
import socketserver
import time,json
from ChatAgent import AgentChat

class StreamHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # 允许所有来源
        self.send_header('Access-Control-Allow-Origin', '*')
        # 允许发送的头信息
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        # 允许的方法
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        # 响应类型
        self.send_header('Content-Length', '0')
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.send_response(204)  # No Content
    def do_GET(self):
        self.send_header('Access-Control-Allow-Origin:', '*')
        self.end_headers()
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin:', '*')
        self.end_headers()
        
        content_length = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_length)
        self.send_stream("test")
        self.handle_msg_request(post_body)
        
    def send_stream(self,text:str):
        message = f"data: {text}\n\n"
        self.wfile.write(message.encode('utf-8'))
        self.wfile.flush()
    def send_end(self,text:str):
        #在客户端监听end事件，表示结束
        end_message = "event: end\ndata: Stream ended\n\n"
        self.wfile.write(end_message.encode('utf-8'))
        self.wfile.flush()

    def handle_msg_request(self,post_body) -> None:
        data = json.loads(post_body)
        try:
            data = json.loads(post_body)
            print("data loaded:",data)
            msgs = data['messages']
            print("messages loaded:",msgs)
            print("message loaded:",msgs[-1]['content'])
            AgentChat(self).chat(msgs[-1]['content'])
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except KeyError as e:
            self.send_error(400, "Invalid KEY")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")

if __name__ == "__main__":
    PORT = 8000
    with socketserver.TCPServer(("", PORT), StreamHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()
