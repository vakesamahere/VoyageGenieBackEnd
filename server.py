from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import json

from dotenv import load_dotenv
import logging,os

load_dotenv()
api_key = os.getenv('API_KEY_DEEPSEEK')
print(api_key)
url='https://api.deepseek.com/chat/completions'

headers={
    'Authorization': f"Bearer {api_key}",
    'Content-Type': 'application/json'
}
model_name="deepseek-chat"

tool_set1 = [
    {
        "type":"function",
        "function":{
            "name": "get_weather",
            "description": "Determine weather in my location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state e.g. 北京, tokyo"
                    }
                },
                "required": [
                    "location"
                ]
            }
        }
    }
],

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # POST JSON
        content_length = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_length)
        self.handle_msg_request(post_body)
    def handle_msg_request(self,post_body) -> None:
        data = json.loads(post_body)
        try:
            data = json.loads(post_body)
            print("data loaded:",data)
            msgs = data['messages']
            print("messages loaded:",msgs)

            # openai interface
            '''
            request_body=json.dumps({
                "model": model_name,
                "messages": msgs,
                "stream": False,
                "tools": tool_set1
            })

            print("request body:",request_body)
            
            response_data = self.send_post_request(url, headers, request_body)
            print("Type of response:",type(response_data))
            print("Response:",response_data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
            '''
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except KeyError as e:
            self.send_error(400, "Invalid KEY")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")
    def send_post_request(self,url, headers, body):
        try:
            response = requests.post(url, headers=headers, data=body)
            response.raise_for_status()  # Raise an exception for HTTP errors
            print("Response Status Code:", response.status_code)
            print("Response Body:", response.text)
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)
        return response.text

def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
