import http.server
import socketserver
import time
import json
from ChatAgent import AgentChat
import logging
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别
    filename='app.log',   # 指定日志输出文件
    filemode='w',         # 模式，'w'为覆盖模式，'a'为追加模式
    format='%(name)s - %(levelname)s - %(message)s'  # 定义日志格式
)

class StreamHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # 允许所有来源
        self.send_header('Access-Control-Allow-Origin', '*')
        # 允许发送的头信息
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        # 允许的方法
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Content-Length', '0')
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.send_response(204)  # No Content

    def do_GET(self):
        logging.debug("收到GET请求")
        try:
            # Your existing code to handle GET request
            self.wfile.write("message".encode('utf-8'))
        except ConnectionAbortedError as e:
            print(f"Connection was aborted: {e}")
            # Perform any necessary cleanup or log the error
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Handle other potential exceptions

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        content_length = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_length)

        try:
            data = json.loads(post_body)
            print("data loaded:", data)
            msgs = data['messages']
            print("messages loaded:", msgs)
            print("message loaded:", msgs[-1]['content'])

            # 假设 AgentChat 类有一个 chat 方法
            response = AgentChat(self).chat(msgs[-1]['content'])
            self.send_stream(response)

        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except KeyError as e:
            self.send_error(400, "Invalid KEY")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")

    def send_stream(self, text: str):
        # SSE
        message = f"data: {text}\n\n"
        self.wfile.write(message.encode('utf-8'))
        self.wfile.flush()

if __name__ == "__main__":
    PORT = 8000
    with socketserver.TCPServer(("", PORT), StreamHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()