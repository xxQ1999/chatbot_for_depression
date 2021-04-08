
# coding=utf-8

import os
import getConfig
import jieba
#结巴分词

gConfig = {}

gConfig=getConfig.get_config()

conv_path = gConfig['resource_data']
 
if not os.path.exists(conv_path):
	
	exit()
#就是将训练集的数据识别读取并存入一个List
convs = []  # 用于存储对话的列表
with open(conv_path,'r',encoding='utf-8') as f:
	one_conv = []        # 存储一次完整对话
	for line in f:
		line = line.strip('\n').replace('/', '')#去除换行符，并将原文件中已经分词的标记去掉，重新用结巴分词.
		if line == '':
			continue
		if line[0] == gConfig['e']:
			if one_conv: 
				convs.append(one_conv)
			one_conv = []
		elif line[0] == gConfig['m']:
			one_conv.append(line.split(' ')[1])#将一次完整的对话存储下来
#训练集的对话进行分类，分为问和答，作为encoder和decoder的熟练数据
seq = []        

for conv in convs:
	if len(conv) == 1:
		continue
	if len(conv) % 2 != 0:  
		conv = conv[:-1]
	for i in range(len(conv)):
		if i % 2 == 0:
			conv[i]=" ".join(jieba.cut(conv[i]))#使用jieba
			conv[i+1]=" ".join(jieba.cut(conv[i+1]))
			seq.append(conv[i]+'\t'+conv[i+1])

seq_train = open(gConfig['seq_data'],'w',encoding='utf-8') 

for i in range(len(seq)):
   seq_train.write(seq[i]+'\n')
 
   if i % 1000 == 0:
      print(len(range(len(seq))), '处理进度：', i)
 
seq_train.close()



