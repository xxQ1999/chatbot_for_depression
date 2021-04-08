from face import face_expression
import socket
import threading
import time
from bixin import predict
import sys


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
        s.bind(('192.168.1.5', 6668))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print('Waiting connection...')

    while 1:
        conn, addr = s.accept()
        t = threading.Thread(target=deal_data, args=(conn, addr))
        t.start()



def deal_data(conn, addr):

    print('Accept new connection from {0}'.format(addr))
    global cnt, emotion
    now = time.time()
    size = conn.recv(10)  # 以10为单位进行接收图片大小信息
    size_str = str(size, encoding="utf-8")  #将Byte流转string
    size_str = size_str.strip()
    file_size = int(size_str)      #获取图片文件大小
    print(size_str)
    if file_size != 0:
        print("接收到数据", file_size, "int")
        picpath = "1.jpg"
        f = open(picpath, "wb")#打开文件准备写入
    has_size = 0     #已接收数据大小
    while True:
        if file_size == has_size:#如果接收的数据足够
          break
        res_data = file_size - has_size
        if res_data >= 1024:
            data = conn.recv(1024)
        else:
            data = conn.recv(res_data)
        f.write(data) #写入文件
        data_size = len(data)
        has_size = has_size + data_size
        print("接收", has_size)
    f.close() #关闭文件
    print("成功接收")
    print("图片储存位置:", picpath)
    x = face_expression(picpath)
    if x == 0:
        emotion = "0\n"
    else:
        emotion = x + '\n'
    print(emotion)
    conn.send(emotion.encode())
    print("fasong")
    time.sleep(1)


if __name__ == '__main__':
    socket_service()

