
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
        self.events=[]

    def cache_load(self,string):
        self.cache_string+=string

    def cache_out(self):
        output=self.cache_string
        self.cache_string=""
        return output
    
    def event_cache_load(self,content:str):
        self.events.append(content)
    
    def event_cache_out(self):
        if len(self.events):
            output = self.events.pop(0)
            return output
        else:
            return ""
    
    def deq(self):
        if not self.tokens:
            time.sleep(0.1)
            return False
        item = self.tokens[0]
        self.tokens.pop(0)
        return item
    
    def enq(self,item):
        self.tokens.append(item)

    def test(self,context):
        print(context)

# def get_message():
#     """this could be any function that blocks until data is ready"""
#     time.sleep(1)
#     s = time.ctime(time.time())
#     return json.dumps(['当前时间：' + s , 'a'], ensure_ascii=False)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/chat',methods=['POST'])
async def streama():
    data = request.get_json()
    msg=data.get('message',"")
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
    loop.run_in_executor(executor,run_crew,r,msg)

    def eventStream():
        id = 0
        flag=0
        sum = 0
        while True:
            time.sleep(1)
            data=r.cache_out()
            if data != '':
                yield 'id: {}\nevent: add\ndata: {}\n\n'.format(id,data)
                id+=1
                flag = 1
            event=r.event_cache_out()
            if event !='':
                yield 'id: {}\nevent: event\ndata: {}\n\n'.format(id,event)
                id+=1
                flag = 1
            if flag == 0:
                sum +=1
            else:
                sum = 0
            if sum > 180:
                return
    return Response(eventStream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=6000)