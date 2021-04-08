import execute
import time
import threading
import jieba

"""定义应答函数，用于获取输入信息并返回相应的答案"""
def reply(req_msg):
# 从请求中获取参数信息
   # req_msg = request.form['msg']
# 将语句使用结巴分词进行分词
    req_msg=" ".join(jieba.cut(req_msg))
    # 调用decode_line对生成回答信息
    res_msg = execute.predict(req_msg)
    #将unk值的词用微笑符号袋贴
    res_msg = res_msg.replace('_UNK', '^_^')
    res_msg=res_msg.strip()
    
    # 如果接受到的内容为空，则给出相应的回复
    if res_msg == ' ':
      res_msg = '请与我聊聊天吧'
    print(res_msg)
    return res_msg


if __name__ == "__main__":
    while True:
        print("输入：")
        a = input()
        if a == 'exit':
            break
        reply(a)




