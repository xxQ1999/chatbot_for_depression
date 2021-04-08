from analyze_attr import get_qgxs
from data_process import analysis_sentence
import pandas as pd
import random
from tf_reply import reply
from analyze_attr import clean_zh_text
from emotion_rule import r1_greetings
from emotion_rule import r2_goodbye
from emotion_rule import r3_thank
from emotion_rule import sub_entity1_and_predicate
from emotion_rule import sub_entity2_and_predicate
from emotion_rule import PreEmotion__DenyAdv
from emotion_rule import sub_self_and_pre
from emotion_rule import sub_other1_and_pre
from emotion_rule import sub_other2_and_pre
from emotion_rule import sub_entity_and_obj
from emotion_rule import delta_time
from emotion_rule import emotion_polarity
from emotion_rule import self_boring
from emotion_rule import sub_belief
from emotion_rule import suicide_answer
from analyze_attr import sign_sub
from analyze_attr import sign_predicate
from analyze_attr import sign_obj_predicate
from analyze_attr import sign_adverbial
from analyze_attr import sign_ADV_Relation
from analyze_attr import get_qgxs
from special_rule import r3_exam
from special_rule import r4_class
from special_rule import r5_homework
from special_rule import r6_project
from special_rule import r7_design
from special_rule import r8_weather
from special_rule import r9_parent
from special_rule import r10_classmate
from special_rule import r11_roommate
from special_rule import r12_friends
from special_rule import r13_lover
from special_rule import r14_teacher
from special_rule import r15_social
from special_rule import r16_job
from special_rule import r17_outlooking
from special_rule import r18_movies
from special_rule import r100_anything
from special_rule import r19_robot
from special_rule import r20_mood
from special_rule import r21_fail
from special_rule import r22_ill
from special_rule import r23_eat
from special_rule import r24_sleep
from special_rule import r25_goodnight
from special_rule import r26_daydream
from special_rule import r27_profession
from special_rule import r28_sing
from special_rule import r29_thirty
from special_rule import r30_boring
from special_rule import r31_lies
from special_rule import r32_graduate
from special_rule import r33_game
from special_rule import r34_taobao
from special_rule import r35_festival
from special_rule import r36_joke
from special_rule import r37_money
from special_rule import r38_scholars
from special_rule import r39_fruit
from special_rule import r40_veg
from special_rule import r41_yjs
from special_rule import r42_gwy
from special_rule import r43_birthday
from special_rule import r44_pet
from special_rule import r45_ncov
from class_check import care_txt
from class_check import ending_txt
from class_check import yueqi_txt

import jieba

MOOD = 0


class info(object):
    def __init__(self, r, w, h, pt):
        self.words = w              # 词
        self.pos_tags = pt          # 词性
        self.head = h               # 首部
        self.relation = r           # 关系
        # 存父子节点的索引
        self.sbv = []               # 主谓
        self.vob = []               # 动宾
        self.att = []               # 定中
        self.adv = []               # 状中
        self.com = []               # 动补 说明动作的状态、结果、程度等
        self.hed = []               # 核心关系
        self.coo = []
        self.pob = []               # 并列
        self.attr_dict_list = []
        self.seq = ""

    # 存主谓宾结构
    def extract_attr(self, r_, w_, h_):
        pre_attribute_index = -1
        for index, z in enumerate(zip(r_, w_, h_)):
            if z[0] == "SBV":
                self.sbv.append((index, z[2] - 1))  # index是主语的索引，h是谓语的索引
            elif z[0] == "VOB":
                self.vob.append((index, z[2] - 1))  # index是宾语的索引，h是谓语的索引
            elif z[0] == "ATT":
                self.att.append((index, z[2] - 1))  # index是定语的索引，h是宾语的索引
            elif z[0] == "ADV":
                self.adv.append((index, z[2] - 1))  # index是状语的索引，h是谓语的索引
            elif z[0] == "CMP":
                self.com.append((index, z[2] - 1))  # index是补语的索引，h是谓语的索引（新增）
            elif z[0] == "HED":
                self.hed.append((index, z[2] - 1))  # index是动词的索引, h是root(-1)
            elif z[0] == "COO":
                self.coo.append((index, z[2] - 1))  # index是下一个并列词的索引， h是这个词的索引
            elif z[0] == "POB":
                self.coo.append((index, z[2] - 1))  # index是并列词的索引， h是和的索引

        # 生成occ需要计算的1至多组句法成分
        if self.sbv is not None:
            # 主谓
            '''
            for sbv_subject_index, sbv_predicate_index in self.sbv:
                attr_dict = {"subject": self.words[sbv_subject_index],
                             "predicate": self.words[sbv_predicate_index],
                             "adverbial": None, "object": None,
                             "sub_attribute": None, "obj_attribute": None,
                             "complement": None, "com_adverbial": None}    # "complement"和"com_adverbial"为补充
             '''
            for sbv_subject_index, sbv_predicate_index in self.sbv:
                attr_dict = {"subject": [self.words[sbv_subject_index], -1000],
                             "predicate": [[self.words[sbv_predicate_index]], -1000],
                             "adverbial": [[], -1000], "object": [[], -1000],
                             "sub_attribute": [[], -1000], "obj_attribute": [[], -1000],
                             "obj_complement":[[],-1000],
                             "complement": [[], -1000], "adverbial_com": [[], -1000]}  # "complement"和"com_adverbial"为补充

                #（补充）寻找额外的谓语
                for index, z in enumerate(zip(r_, w_, h_)):
                    if z[0] == "COO" and self.words[z[2] - 1] in attr_dict["predicate"][0]:
                        attr_dict["predicate"][0].append(self.words[index])
                # 状语
                for adv_adverbial_index, adv_predicate_index in self.adv:
                    if sbv_predicate_index == adv_predicate_index:
                        attr_dict["adverbial"][0].append(self.words[adv_adverbial_index])
                for vob_object_index, adv_predicate_index in self.vob:
                    if sbv_predicate_index == vob_object_index:
                        attr_dict["adverbial"][0].append(self.words[adv_predicate_index])
                # 补充（补语）
                for pre_attribute_index, predicate_index in self.com:
                    if predicate_index == sbv_predicate_index:
                        attr_dict["complement"][0].append(self.words[pre_attribute_index])
                # 补充(补语对应的状语)
                for adv_adverbial_index_1, adv_predicate_index_1 in self.adv:
                    if adv_predicate_index_1 == pre_attribute_index:
                        attr_dict["adverbial_com"][0].append(self.words[adv_adverbial_index_1])

                # 定语
                for att_attribute_index, att_subject_index in self.att:
                    if sbv_subject_index == att_subject_index:
                        attr_dict["sub_attribute"][0].append(self.words[att_attribute_index])
                # 找宾语
                for vob_object_index, vob_predicate_index in self.vob:
                    if sbv_predicate_index == vob_predicate_index:
                        attr_dict["object"][0].append(self.words[vob_object_index])
                        # 定语
                        for att_attribute_index, att_object_index in self.att:
                            if att_object_index == vob_object_index:
                                attr_dict["obj_attribute"][0].append(self.words[att_attribute_index])
                        #
                        for object_com, object_index in self.com:
                            if object_index == vob_object_index:
                                attr_dict["obj_complement"][0].append(self.words[object_com])
                        break
                self.attr_dict_list.append(attr_dict)


def main_process(txt, MOOD):
    generator = analysis_sentence(txt)                          # 句型分析
    for word, head_num_list, pos_tag, relation_list in generator:
        #print(word)
        #print(head_num_list)
        #print(pos_tag)
        #print(relation_list)
        s1 = info(relation_list, word, head_num_list, pos_tag)
        #print(s1.words)
        #print(s1.head)
        #print(s1.pos_tags)
        #print(s1.relation)
        s1.extract_attr(relation_list, word, head_num_list)

        #print(s1.att)
   #print(s1.attr_dict_list)

    flag_answer = 0
    answer = ""
    s1.seq = txt
    flag_answer = rule_judge(s1, MOOD)

    if flag_answer == 0:
        for attr_dict_list in s1.attr_dict_list:
            #print(attr_dict_list)
            if self_boring(attr_dict_list):             # 用户很无聊
                answer = self_boring(attr_dict_list)
                print("boring")
            elif sub_belief(attr_dict_list):            # 用户没有信仰
                answer = sub_belief(attr_dict_list)
                print("belief")
            elif sub_entity1_and_predicate(attr_dict_list):
                answer = sub_entity1_and_predicate(attr_dict_list)
                print("心情主体")
            elif sub_entity2_and_predicate(attr_dict_list):
                answer = sub_entity2_and_predicate(attr_dict_list)
                print("身体是主体")
            elif PreEmotion__DenyAdv(attr_dict_list):
                answer = PreEmotion__DenyAdv(attr_dict_list)
                print("我和情绪")
            elif sub_self_and_pre(attr_dict_list):
                answer = sub_self_and_pre(attr_dict_list)
                print("主语是自己，谓语动词")
            elif sub_other1_and_pre(attr_dict_list):
                answer = sub_other1_and_pre(attr_dict_list)
                print("主语是你，谓语动词")
            elif sub_other2_and_pre(attr_dict_list):
                answer = sub_other2_and_pre(attr_dict_list)
                print("主语是他人，谓语动词")
            elif sub_entity_and_obj(attr_dict_list):
                answer = sub_entity_and_obj(attr_dict_list)
                print("主语是自己、宾语")
            elif delta_time(attr_dict_list, s1):
                answer = delta_time(attr_dict_list, s1)
                print("主语是自己，有时间差")
            #  补充上不同情绪对应的安慰的话
            else:
                answer = emotion_polarity(s1, txt)
                print("情绪极性")
                #这里
                #if answer == "":
                #    answer = "对不起，我没明白您的问话，换个问题好吗？"
        if answer == 0 or answer is None or answer == "" or len(clean_zh_text(answer)) == 0:
            answer = emotion_polarity(s1, txt)
        if answer == 0 or answer is None or answer == "" or len(clean_zh_text(answer)) == 0:
            answer = reply(s1.seq)
            answer = answer.rstrip('。').rstrip('~').rstrip('？').rstrip('！').rstrip('，')
            if len(answer) > 10:
                answer = "我没听明白欸"
        if answer == "" or answer is None or answer == 'a' or len(clean_zh_text(answer)) == 0 or "你妈" in answer or \
                "神经病" in answer or "有病" in answer or "个头" in answer or "去你的" in answer or "死" in answer or \
                "草" in answer or "滚" in answer or "黄" in answer or "傻" in answer or "逼" in answer or "屁" in answer or \
                "粑" in answer:
            answer = "我没听明白诶"
    else:
        answer = flag_answer
    # print(answer)
    return answer


def pre_process(s):
    answer = ""
    result = list(jieba.lcut(s))
    print(result)
    neg_path = "dict/emotion_dict/neg_all_dict.csv"
    exam_path = "dict/special_judge/exam/exam.csv"
    suicide_path = "dict/special_judge/suiside.csv"
    neg_df = pd.read_csv(neg_path)
    exam_df = pd.read_csv(exam_path)
    suicide_df = pd.read_csv(suicide_path)
    neg_list = neg_df.loc[:, 'word'].tolist()
    exam_list = exam_df.loc[:, 'word'].tolist()
    suicide_list = suicide_df.loc[:, 'word'].tolist()
    del exam_df
    del neg_df
    del suicide_df
    pos = 0
    exam = 0
    suicide = 0
    for word in result:
        if word in exam_list:
            exam = 1
        if word in suicide_list:
            suicide = 1
        if word in neg_list:
            pos = -1
        if exam != 0 and pos != 0:
            break
        if suicide != 0:
            break
    if suicide == 1:
        answer = suicide_answer()
        print(answer)
        return answer
    '''if exam == 1:
        if pos == -1:
            answer = "虽然有点难的样子，但是我相信你哦！不管是学习上还是别的，只要我们认真的去做了，就是最好的！"
        else:
            answer = "我知道你可以的~因为认真努力的你是世界上最好看的。"
        print(answer)
        '''
    return answer


# 之前写的回答匹配
def chat_answer(msg, MOOD):
    # answer = pre_process(msg)
    # if answer == "":
    answer = main_process(msg, MOOD)
    return answer


# rule
def rule_judge(s, MOOD):
    # 主题模板
    # 1 打招呼
    # 2 再见
    # 3 考试: 考的简单 考的困难 成绩好 成绩差 担心考试 作弊 6
    # 4 上课: 听得懂 听不懂 专心 不专心 4
    # 5 作业: 会做 不会做 简单 困难 抄袭 多 少 6
    # 6 项目: 会做 不会做 简单 困难 抄袭 5
    # 7 毕业设计: 会做 不会做 2
    # 8 天气: 好 一般 坏 3
    # 9 父母关系: 父母之间吵架 父母和自己吵架 父母不关心自己 3
    # 10 寝室关系: 室友之间不和 室友和自己不和 2
    # 11 同学关系: 同学之间不和 同学和自己不和 2
    # 12 朋友关系: 朋友少 朋友多 朋友与自己的矛盾 3
    # 13 恋人关系: 吵架 相亲相爱 分手 失恋 和好 5
    # 14 暗恋关系: 告白成功 告白失败 犹豫不决 3
    # 15 老师关系: 和睦 不和睦 2
    # 16 社交问题: 社交恐惧 社交厌倦 被欺负/嘲笑/辱骂/殴打/孤立 3
    # 17 就业烦恼: 职业方向 薪酬 工作地点 就业困难 就业恐惧 5
    # 18 经济烦恼: 兼职 家庭经济 诈骗 消费 4
    # 19 自信问题: 不自信
    # 20 外貌烦恼: 脸不好看 身材不好 2
    # 21 电影
    # 22 电视剧
    # 23 游戏
    # 24 购物
    # 25 身体素质:　生病 健康 疲惫 3
    # 26 负面泛泛: 只含有以下关键词：压力 心情 情绪 [负面情绪词]
    # 27 正面泛泛: 只含有以下关键词：心情 [正面情绪词]
    # 28 小说
    # 29 在干嘛
    # 30 机器人 姓名 性别 爱好 年龄 家庭住址(你)
    # 31 无法识别对话: 1. 深度学习 2. 返回"听不懂"
    a = r1_greetings(s)
    if a == 0:
        a = r2_goodbye(s)
    if a == 0:
        a = r3_thank(s)
    if a == 0:
        a = r100_anything(s)
        print(a)
    if a == 0:
        a = care_txt(s, MOOD)
    if a == 0:
        a = r3_exam(s)
    if a == 0:
        a = r4_class(s)
    if a == 0:
        a = r5_homework(s)
    if a == 0:
        a = r6_project(s)
    if a == 0:
        a = r7_design(s)
    if a == 0:
        a = r8_weather(s, MOOD)
    if a == 0:
        a = r20_mood(s)
    if a == 0:
        a = r21_fail(s)
    if a == 0:
        a = r22_ill(s)
    if a == 0:
        a = r23_eat(s)
    if a == 0:
        a = r24_sleep(s)
    if a == 0:
        a = r25_goodnight(s)
    if a == 0:
        a = r26_daydream(s)
    if a == 0:
        a = r27_profession(s)
    if a == 0:
        a = r28_sing(s)
    if a == 0:
        a = r29_thirty(s)
    if a == 0:
        a = r30_boring(s)
    if a == 0:
        a = r31_lies(s)
    if a == 0:
        a = r32_graduate(s)
    if a == 0:
        a = r33_game(s)
    if a == 0:
        a = r34_taobao(s)
    if a == 0:
        a = r35_festival(s)
    if a == 0:
        a = r36_joke(s)
    if a == 0:
        a = r37_money(s)
    if a == 0:
        a = r38_scholars(s)
    if a == 0:
        a = r39_fruit(s)
    if a == 0:
        a = r40_veg(s)
    if a == 0:
        a = r41_yjs(s)
    if a == 0:
        a = r42_gwy(s)
    if a == 0:
        a = r43_birthday(s)
    if a == 0:
        a = r44_pet(s)
    if a == 0:
        a = r45_ncov(s)
    if a == 0:
        a = r9_parent(s)
        print("9")
    if a == 0:
        a = r13_lover(s)
        print("13")
    if a == 0:
        a = r10_classmate(s)
        print("10")
    if a == 0:
        a = r11_roommate(s)
        print("11")
    if a == 0:
        a = r12_friends(s)
        print("12")
    if a == 0:
        a = r14_teacher(s)
        print("14")
    if a == 0:
        a = r15_social(s)
        print("15")
    if a == 0:
        a = r16_job(s)
    print(a)
    if a == 0:
        a = r17_outlooking(s)
        print(">>>>>")
    if a == 0:
        a = r18_movies(s)
    if a == 0:
        a = r19_robot(s)
    if a == 0:
        a = yueqi_txt(s)
    if a == 0:
        a = ending_txt(s)
    return a


def test_ltp(txt):
    generator = analysis_sentence(txt)                          # 句型分析
    for word, head_num_list, pos_tag, relation_list in generator:
        print(word)
        print(head_num_list)
        print(pos_tag)
        print(relation_list)
        s1 = info(relation_list, word, head_num_list, pos_tag)
        s1.extract_attr(relation_list, word, head_num_list)
        print(s1.sbv)
   #print(s1.attr_dict_list)


if __name__ == "__main__":
   # main_process("我抱着沙发，睡眼昏花，凌乱头发，却渴望自由与潇洒")
   # answer = pre_process("身体不舒服。") # 考试、成绩、分数
   # if answer == "":
   #     answer = main_process("身体不舒服。")
   while 1:
        print("输入：")
        msg = input()
        if msg == 'exit':
            break
        # msg2 = clean_zh_text(msg)
        # x = r1_greetings(msg2)
        # if x == 0:
        #    x = r2_goodbye(msg2)
        # if x == 0:
        #     x = r2_thank(msg2)
        # if x == 0:
        # x = main_process(msg)
        x = chat_answer(msg)
        print(x)
        print("结束.")

