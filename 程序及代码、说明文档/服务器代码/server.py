"""
file: service.py
socket service
"""

import socket
import threading
import time
import sys
from analyze_attr import clean_zh_text
import os
from app import chat_answer
from tf_reply import reply
from tensorflow.python.client import device_lib
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "99"

cnt = 0
msg = ""
answer = ""
emotion = ""
emotion_direction = 0

def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 防止socket server重启后端口被占用（socket.error: [Errno 98] Address already in use）
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('192.168.1.5', 6666))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print('Waiting connection...')

    while 1:
        conn, addr = s.accept()
        t = threading.Thread(target=deal_data, args=(conn, addr))
        t.start()
        #print("Accept from"+format(addr))
        #data=conn.recv(1024)
        #print(format(addr)+"send data is :"+data.decode())
        #mydata = "good\n"
        #conn.send(mydata.encode())
        #print("sendover")

#你好

def deal_data(conn, addr):
    global msg, cnt, answer
    print('Accept new connection from {0}'.format(addr))
    #data = "good\n"
    #conn.send(data.encode())
    if cnt == 0:
        data = conn.recv(1024)
        print('{0} client send data is {1}'.format(addr, data.decode()))  # b'\xe8\xbf\x99\xe6\xac\xa1\xe5\x8f\xaf\xe4\xbb\xa5\xe4\xba\x86'
        msg = data.decode()

    else:
        # 这里要send自己的
        answer = deal_txt(msg)
        print(msg)
        if answer == "" or answer is None or answer == 'a' or len(clean_zh_text(msg)) == 0:
            answer = "哎，我太笨了听不懂"
        conn.send(answer.encode())
        #print("send:"+answer)
    cnt = (cnt+1) % 2
    #time.sleep(1)
    conn.close()


def deal_txt(msg):
    answer = chat_answer(msg)
    return answer

if __name__ == '__main__':
    socket_service()
    #print(device_lib.list_local_devices())

