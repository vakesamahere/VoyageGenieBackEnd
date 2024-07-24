
import json
import time
import logging
from flask import Flask, request,stream_with_context,jsonify
from flask import Response
from flask import render_template
import threading
from flask_cors import CORS,cross_origin
import asyncio
from main import run_crew
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
CORS(app)

DELAY=0.05

executor = ThreadPoolExecutor(max_workers=5)

class Receiver:
    def __init__(self) -> None:
        self.tokens=[]
        self.cache_string=""

    def cache_load(self,string):
        self.cache_string+=string

    def cache_out(self):
        output=self.cache_string
        self.cache_string=""
        return output
    
    def deq(self):
        if not self.tokens:
            time.sleep(0.1)
            return False
        item = self.tokens[0]
        self.tokens.pop(0)
        return item
    def enq(self,item):
        self.tokens.append(item)

# def get_message():
#     """this could be any function that blocks until data is ready"""
#     time.sleep(1)
#     s = time.ctime(time.time())
#     return json.dumps(['当前时间：' + s , 'a'], ensure_ascii=False)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/stream',methods=['POST'])
async def streama():
    data = request.get_json()
    logging.debug(data)
    r=Receiver()
    r.cache_load("test cache loading success")
    print(r.cache_out())

    def test(rec):
        time.sleep(5)
        print("awake")
        rec.cache_load('asyn info')

    loop=asyncio.get_event_loop()
    # loop.run_in_executor(executor,test,r)
    loop.run_in_executor(executor,run_crew,r)

    def eventStream():
        id = 0
        while True:
            time.sleep(1)
            data=r.cache_out()
            if data == '':
                continue
            if data == '<END>':
                yield 'id: {}\nevent: add\ndata: {}\n\n'.format(id,data)
                break
            yield 'id: {}\nevent: add\ndata: {}\n\n'.format(id,data)
    return Response(eventStream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True)

