#-*-coding:utf-8-*-
from flask import Flask
from flask import request
import os
import socket
import threading
import time
import sys
from analyze_attr import clean_zh_text
import os
from app import chat_answer
# from tf_reply import reply
# from tensorflow.python.client import device_lib


msg = ""
answer = ""
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

@app.route('/')
def test():
    return '服务器正常运行'



#此方法处理用户文本
@app.route('/chat', methods=['POST'])
def chat():
    # username=request.form['username']
    # password=request.form['password']

    print('Accept new connection')
    msg = request.form['chat']
    print("client send data is "+msg)
    MOOD = msg[0]
    # print('username:'+username)
    # print('password:'+password)
    msg = msg[1:]
    answer = deal_txt(msg, MOOD)
    if answer == "" or answer is None or answer == 'a' or len(clean_zh_text(msg)) == 0:
        answer = "哎，我太笨了听不懂"
    print("send: "+answer)
    return answer


def deal_txt(msg, MOOD):
    answer = chat_answer(msg, MOOD)
    return answer


if __name__ == '__main__':
    app.run(host='0.0.0.0')

