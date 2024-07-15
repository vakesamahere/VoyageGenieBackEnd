from flask import Flask, Response, stream_with_context, request
from flask_cors import CORS
import time
import asyncio
from asyncio import Queue

app = Flask(__name__)
CORS(app)  # 允许所有域名访问

# 异步生成器函数，从队列 A 中生成内容
async def unsend_tokens(A: Queue):
    while True:
        item = await A.get()
        if item == 'end':
            return
        else:
            yield f"Token: {item}<br>"

# 处理流式请求，使用 unsend_tokens(A) 生成器函数
@app.route('/stream', methods=['POST'])
def stream():
    def generate():
        yield "Part 1 of the response<br>"
        time.sleep(1)
        yield "Part 2 of the response<br>"
        time.sleep(10)
        yield "Part 3 of the response<br>"
        
    return Response(stream_with_context(generate()), content_type='text/html')

def add_to_queue(A: asyncio.Queue, item):
    asyncio.get_event_loop().call_soon_threadsafe(A.put_nowait, item)
    
if __name__ == '__main__':
    app.run(debug=True)
