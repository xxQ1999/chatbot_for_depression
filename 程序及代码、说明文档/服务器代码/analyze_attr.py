import pandas as pd
from data_process import analysis_sentence
import re


# 英文文本符号去除
def clean_en_text(text):
    # 留下英文、数字和空格
    comp = re.compile('[^A-Z^a-z^0-9^ ]')
    return comp.sub('', text)


# 中文文本
def clean_zh_text(text):
    # 留下英文、中文和数字
    comp = re.compile('[^A-Z^a-z^0-9^\u4e00-\u9fa5]')
    return comp.sub('', text)


#情绪类型计算
def get_qgxs(s1):
    # print('get_qgxs')

    angry_qgxs = 0  # 情感系数
    evil_qgxs = 0
    fear_qgxs = 0
    sad_qgxs = 0
    shocked_qgxs = 0
    not_happy_qgxs = 0
    not_good_qgxs = 0

    for word in s1.words:
        angry_qgxs = angry_qgxs + get_some_qgxs('dict\\emotion_dict2\\angry.txt', word,s1) 
        evil_qgxs = evil_qgxs + get_some_qgxs('dict\\emotion_dict2\\evil.txt', word, s1) 
        fear_qgxs = fear_qgxs + get_some_qgxs('dict\\emotion_dict2\\fear.txt', word, s1) 
        sad_qgxs = sad_qgxs + get_some_qgxs('dict\\emotion_dict2\\sad.txt', word,s1) 
        shocked_qgxs = shocked_qgxs + get_some_qgxs('dict\\emotion_dict2\\shocked.txt', word, s1)
        not_happy_qgxs = not_happy_qgxs - 1 * get_some_qgxs('dict\\emotion_dict2\\happy.txt', word, s1)
        not_good_qgxs = not_good_qgxs - get_some_qgxs('dict\\emotion_dict2\\good.txt', word, s1)
    '''
    print('angry_qgxs = ' + str(angry_qgxs))
    print('evil_qgxs = ' + str(evil_qgxs))
    print('fear_qgxs = ' + str(fear_qgxs))
    print('sad_qgxs = ' + str(sad_qgxs))
    print('shocked_qgxs = ' + str(shocked_qgxs))
    print('not_happy_qgxs = ' + str(not_happy_qgxs))
    print('not_good_qgxs = ' + str(not_good_qgxs))
    '''
  
    yield angry_qgxs, evil_qgxs, fear_qgxs, sad_qgxs, shocked_qgxs, not_happy_qgxs, not_good_qgxs


def sign_sub(sub_list):     # 自身--1 物体--0 他人-- -1 物体（1）-- 2 他人（你）--3
    sub_self_path = 'dict/subject/self.csv'
    sub_other1_path = 'dict/subject/other.csv'
    sub_other2_path = 'dict/subject/other_1.csv'
    sub_entity1_path = 'dict/subject/entity.csv'
    sub_entity2_path = 'dict/subject/entity_1.csv'
    df_self = pd.read_csv(sub_self_path)
    df_other1 = pd.read_csv(sub_other1_path)
    df_other2 = pd.read_csv(sub_other2_path)
    df_entity1 = pd.read_csv(sub_entity1_path)
    df_entity2 = pd.read_csv(sub_entity2_path)
    sub_self_list = df_self.loc[:, "word"].tolist()
    sub_other_list1 = df_other1.loc[:, "word"].tolist()
    sub_other_list2 = df_other2.loc[:, "word"].tolist()
    sub_entity_list1 = df_entity1.loc[:, "word"].tolist()
    sub_entity_list2 = df_entity2.loc[:, "word"].tolist()
    del df_self
    del df_other1
    del df_other2
    del df_entity1
    del df_entity2
    if sub_list[0] in sub_self_list:
        sub_list[1] = 1 # 我
    elif sub_list[0] in sub_entity_list1:
        sub_list[1] = 0 #物体心情
    elif sub_list[0] in sub_entity_list2:
        sub_list[1] = 2 #身体
    elif sub_list[0] in sub_other_list1:
        sub_list[1] = -1 #别人
    elif sub_list[0] in sub_other_list2:
        sub_list[1] = 3 #你


def sign_predicate(predicate_list, positive_list_path, negative_list_path):      # 积极词性为1， 消极为-1
    pos_df = pd.read_csv(positive_list_path)
    neg_df = pd.read_csv(negative_list_path)
    pos_list = pos_df.loc[:, "word"].tolist()
    neg_list = neg_df.loc[:, "word"].tolist()
    del pos_df
    del neg_df
    for index, pre in enumerate(predicate_list[0]):
        if pre in pos_list:
            predicate_list[1] = 1
        elif pre in neg_list:
            predicate_list[1] = -1
        if predicate_list[1] == 1 or predicate_list[1] == -1:
            break


def sign_obj_predicate(predicate_list, pre_list_path):
    pre_df = pd.read_csv(pre_list_path)
    pre_list = pre_df.loc[:, "word"].tolist()
    del pre_df
    if predicate_list[0] in pre_list:
        predicate_list[1] = 1
    else:
        predicate_list[1] = -1


def sign_adverbial(adverbial_list, adverbial_word_path):                # 否定关键词对应 -1

    deny_df = pd.read_csv(adverbial_word_path)
    word_list = deny_df.loc[:, "word"].tolist()
    adverbial_list[1] = 1
    del deny_df
    for word_adv in adverbial_list[0]:
            if word_adv in word_list:
                adverbial_list[1] = -1



def seek_adv(adv_list):
    time_past_path = 'dict/delta_time/past_time.csv'
    time_now_path = 'dict/delta_time/now_time.csv'
    time_past_df = pd.read_csv(time_past_path)
    time_now_df = pd.read_csv(time_now_path)
    time_past_list = time_past_df.loc[:, 'time'].tolist()
    time_now_list = time_now_df.loc[:, 'time'].tolist()
    del time_past_df
    del time_now_df
    if adv_list[0] in time_past_list and adv_list[1] in time_now_list:       # 先前后后
        return 1
    elif adv_list[1] in time_past_list and adv_list[0] in time_now_list:     # 先后后前
        return -1
    else:                                                                  # 没有前后副词
        return 0


def seek_pre(pre_list):
    positive_path = 'dict/emotion_dict/pos_all_dict.csv'
    negative_path = 'dict/emotion_dict/neg_all_dict.csv'
    positive_df = pd.read_csv(positive_path)
    negative_df = pd.read_csv(negative_path)
    positive_list = positive_df.loc[:, 'word'].tolist()
    negative_list = negative_df.loc[:, 'word'].tolist()
    del positive_df
    del negative_df
    if pre_list[0] in positive_list and pre_list[1] in negative_list:  # 先好后坏
        return -1
    elif pre_list[1] in positive_list and pre_list[0] in negative_list:  # 先坏后好
        return 1
    else:  # 没有前后副词
        return 0

def sign_ADV_Relation(info_entity):
    adv_list = []
    pre_list = []
    for index, relation in enumerate(info_entity.relation):
        if relation == 'ADV':
            adv_list.append(info_entity.words[index])
            header = info_entity.head[index]
            pre_list.append(info_entity.words[header-1])
    if len(adv_list) <= 0:
        return -1
    elif len(adv_list) == 2:
        if seek_adv(adv_list) == 1 and seek_pre(pre_list) == 1:        # 前后+坏好
            return 1
        elif seek_adv(adv_list) == 1 and seek_pre(pre_list) == -1:     # 前后+好坏
            return 2
        elif seek_adv(adv_list) == -1 and seek_pre(pre_list) == 1:     # 后前+坏好
            return 3
        elif seek_adv(adv_list) == -1 and seek_pre(pre_list) == -1:    # 后前+好坏
            return 4


def get_adv(s1, an_qgxs):
    for index, relation in enumerate(s1.relation):
        if relation == 'ADV' or relation == 'CMP':
            an_qgxs = an_qgxs * get_Degree(s1.words[index])
    return an_qgxs


    # 查找某一种情感强度
def get_some_qgxs(path, word, s1):
    an_qgxs = 0
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if (line == (word + '\n')):
                an_qgxs = 1
                # 搜索该节点下的副词
                an_qgxs = get_adv(s1, an_qgxs)
    return an_qgxs


# 获取程度副词的程度系数
def get_Degree(s):
    with open('dict\\degree_dict\\insufficiently.txt', 'r', encoding='utf-8') as f: 
        for line in f:
            if (line == (s + '\n')):
                return 0.5
    with open('dict\\degree_dict\\inverse.txt', 'r', encoding='utf-8') as f:	
        for line in f:
            if (line == (s + '\n')):
               # print('-1' + line)
                return -1
    with open('dict\\degree_dict\\ish.txt', 'r', encoding='utf-8') as f:	
        for line in f:
            if (line == (s + '\n')):
                return 0.8
    with open('dict\\degree_dict\\more.txt', 'r', encoding='utf-8') as f: 
        for line in f:
            if (line == (s + '\n')):
                return 1.5
    with open('dict\\degree_dict\\most.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if (line == (s + '\n')):
                return 2
    with open('dict\\degree_dict\\over.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if (line == (s + '\n')):
                #print('-0.5' + line)
                return -0.5
    with open('dict\\degree_dict\\very.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if (line == (s + '\n')):
                return 3
    return 1
