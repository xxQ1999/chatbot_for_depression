from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from datetime import timedelta
from face import face_expression
import socket
import threading
import time
from bixin import predict
import sys
import os

app = Flask(__name__)

# 输出
@app.route('/')
def hello_world():
    return 'Hello World!'


# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)


# 添加路由
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    print('Accept new connection')
    if request.method == 'POST':
        # 通过file标签获取文件
        f = request.files['file']
        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "msg": "图片类型：png、PNG、jpg、JPG、bmp"})
        # 当前文件所在路径
        basepath = os.path.dirname(__file__)
        # 一定要先创建该文件夹，不然会提示没有该路径
        upload_path = os.path.join(basepath, 'img', secure_filename(f.filename))
        # 保存文件
        f.save(upload_path)
        # 返回上传成功界面
        # return render_template('upload_ok.html')
        print("成功接收")
        x = face_expression(upload_path)
        if x == 0:
            emotion = "空"
        else:
            emotion = x
        print(emotion)
        return emotion
    # 重新返回上传界面
    # return render_template('upload.html')
    return "空"


if __name__ == '__main__':
    app.run(host="0.0.0.0")
