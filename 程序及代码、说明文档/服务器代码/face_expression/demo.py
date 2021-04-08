# /usr/bin/python3
import cv2
import numpy as np
import sys
import tensorflow.compat.v1 as tf
from skimage import io
import os

from model import predict, image_to_tensor, deepnn

tf.disable_v2_behavior()
CASC_PATH = './data/haarcascade_files/haarcascade_frontalface_default.xml'
cascade_classifier = cv2.CascadeClassifier(CASC_PATH)
EMOTIONS = ['angry', 'disgusted', 'fearful', 'happy', 'sad', 'surprised', 'neutral']


# 识别人脸，调整图像大小
def format_image(image):
    # 将图片转化成灰度图片
    if len(image.shape) > 2 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = cascade_classifier.detectMultiScale(
        image,
        scaleFactor=1.3,
        minNeighbors=5
    )
    # 没有面部
    if not len(faces) > 0:
        return None, None
    
    # 识别最大的面部
    max_are_face = faces[0]
    for face in faces:
        if face[2] * face[3] > max_are_face[2] * max_are_face[3]:
            max_are_face = face

    # 将面部数据保存为image
    face_coor = max_are_face
    image = image[face_coor[1]:(face_coor[1] + face_coor[2]), face_coor[0]:(face_coor[0] + face_coor[3])]
   
    # 重构image
    try:
        image = cv2.resize(image, (48, 48), interpolation=cv2.INTER_CUBIC)
    except Exception:
        print("[+} Problem during resize")
        return None, None
    return image, face_coor


# 检测人脸 返回最大面部的坐标
def face_dect(image):

    # 灰度处理
    if len(image.shape) > 2 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = cascade_classifier.detectMultiScale(
        image,
        scaleFactor=1.3,
        minNeighbors=5
    )

    # 没有人脸
    if not len(faces) > 0:
        return None

    # 找到最大的面部    
    max_face = faces[0]
    for face in faces:
        if face[2] * face[3] > max_face[2] * max_face[3]:
            max_face = face
    face_image = image[max_face[1]:(max_face[1] + max_face[2]), max_face[0]:(max_face[0] + max_face[3])]
    
    try:
        image = cv2.resize(face_image, (48, 48), interpolation=cv2.INTER_CUBIC) / 255.
    except Exception:
        print("[+} Problem during resize")
        return None
    return face_image


def resize_image(image, size):
    try:
        image = cv2.resize(image, size, interpolation=cv2.INTER_CUBIC) / 255.
    except Exception:
        print("+} Problem during resize")
        return None
    return image


def draw_emotion():
    pass


def demo(modelPath, showBox = False, image_path="p3.jpg"):

    # 构建模型
    face_x = tf.placeholder(tf.float32, [None, 2304])
    y_conv = deepnn(face_x)
    probs = tf.nn.softmax(y_conv)

    # 存储器
    saver = tf.train.Saver()
    ckpt = tf.train.get_checkpoint_state(modelPath)
    sess = tf.Session()

    # 加载模型
    if ckpt and ckpt.model_checkpoint_path:
        saver.restore(sess, ckpt.model_checkpoint_path)
        print('模型加载成功！')
        # NOTE: Press SPACE on keyboard to capture face.')

    # 加载emoji
    feelings_faces = []
    for index, emotion in enumerate(EMOTIONS):
        feelings_faces.append(cv2.imread('./data/emojis/' + emotion + '.png', -1))
    # video_captor = cv2.VideoCapture(0)

    emoji_face = []
    result = None

    # while True:
    # ret, frame = video_captor.read()
    img = load_image_skimage(image_path)
    # frame = img
    detected_face, face_coor = format_image(img)
    # if showBox:
    #  if face_coor is not None:
    #    [x,y,w,h] = face_coor
    #    cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

    # if cv2.waitKey(1) & 0xFF == ord(' '):

    # 如果存在人脸，就进行表情的识别
    if detected_face is not None:
        # cv2.imwrite('a.jpg', detected_face)
        tensor = image_to_tensor(detected_face)
        #识别人脸的情绪，并计算情绪分类的概率
        result = sess.run(probs, feed_dict={face_x: tensor})
        # print(result)
    face_id = 0
    if result is not None:
        # for index, emotion in enumerate(EMOTIONS):
        # cv2.putText(frame, emotion, (10, index * 20 + 20), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 255, 0), 1)
        # cv2.rectangle(frame, (130, index * 20 + 10), (130 + int(result[0][index] * 100), (index + 1) * 20 + 4),
        #              (255, 0, 0), -1)
        # emoji_face = feelings_faces[np.argmax(result[0])]
        face_id = np.argmax(result[0])
        print(face_emoji(face_id))
        return face_emoji(face_id)
    else:
        return 0
        # for c in range(0, 3):
        # frame[200:320, 10:130, c] = emoji_face[:, :, c] * (emoji_face[:, :, 3] / 255.0) + frame[200:320, 10:130, c] * (1.0 - emoji_face[:, :, 3] / 255.0)
        # cv2.imshow('face', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        # break


def load_image_skimage(filename, isFlatten=False):
    isExit = os.path.isfile(filename)
    if isExit == False:
        print("打开失败!")
    img = io.imread(filename)  # io.save(filename,img)保存文件
    if isFlatten:
        img_flatten = np.array(np.array(img, dtype=np.uint8).flatten())
        return img_flatten  # ,shape(img_flatten)
    else:
        img_arr = np.array(img, dtype=np.uint8)
        return img_arr  # , shape(img_arr)


def face_emoji(id):
    if id == 0:
        return "愤怒"
    elif id == 1:
        return "厌恶"
    elif id == 2:
        return "恐惧"
    elif id == 3:
        return "喜悦"
    elif id == 4:
        return "悲伤"
    elif id == 5:
        return "惊讶"
    else:
        return "平静"
