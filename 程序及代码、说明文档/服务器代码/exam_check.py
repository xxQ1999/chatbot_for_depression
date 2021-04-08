from analyze_attr import get_qgxs
from data_process import analysis_sentence
import pandas as pd
import random
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
from emotion_rule import sign_sub
from analyze_attr import sign_sub
from analyze_attr import sign_predicate
from analyze_attr import sign_obj_predicate
from analyze_attr import sign_adverbial
from analyze_attr import sign_ADV_Relation
from analyze_attr import get_qgxs
import jieba

SBV = "SBV"
ADV = "ADV"
CMP = "CMP"
VOC = 'VOC'
HED = 'HED'
COO = 'COO'

def seek_adv_deny(adv_list, deny_path):
    deny_df = pd.read_csv(deny_path)
    deny_list = deny_df.loc[:, 'word'].tolist()
    del deny_df

    adv_list[1]=1;
    for word_adv in adv_list[0]:
        if word_adv in deny_list:
            adv_list[1] = adv_list[1] * (-1)


# 判断修饰难 的 词 否定返回1 不否定返回 0
def judge_adv_deny(adv, deny_path):
    deny_df = pd.read_csv(deny_path)
    deny_list = deny_df.loc[:, 'word'].tolist()
    del deny_df

    if adv in deny_list:
        return 1
    else:
        return 0


def judge_specific_sub(sub_list, sub_path): # 1 找到 0 没找到 从指定列表找词 是不是存在
    sub_df = pd.read_csv(sub_path)
    my_list = sub_df.loc[:,"word"].tolist()
    del sub_df

    sub_list[1] = 0
    for word_sub in sub_list[0]:
        if word_sub in my_list:
            sub_list[1] = 1
            break

    if sub_list[1] == 1:
        return 1
    else:
        return 0


def is_in(x, path):
    df = pd.read_csv(path)
    my_list = df.loc[:,"word"].tolist()
    del df

    if x in my_list:
        return 1
    else:
        return 0


def find_index(TYPE, temp, word):  # 找关系中对应的下标
    index = []
    if TYPE == SBV:
        for sub_temp, pre_temp in temp.sbv:
            if sub_temp == word:
                index.append(pre_temp)
                # return pre_temp
    elif TYPE == ADV:
        for adv_temp, pre_temp in temp.adv:
            if pre_temp == word:
                index.append(adv_temp)
                # return adv_temp
    elif TYPE == CMP:
        for adv_temp, pre_temp in temp.com:
            if pre_temp == word:
                index.append(adv_temp)

    elif TYPE == COO:
        for adv_temp, pre_temp in temp.coo:
            if pre_temp == word:
                index.append(adv_temp)

    return index


# 判断 x的词性 1:积极 0:中性 -1:消极
def judge_neg_pos(x, neg_path, pos_path):
    neg_df = pd.read_csv(neg_path)
    pos_df = pd.read_csv(pos_path)

    pos_list = pos_df.loc[:, "word"].tolist()
    neg_list = neg_df.loc[:, "word"].tolist()
    del pos_df
    del neg_df

    if x in pos_list:
        return 1
    elif x in neg_list:
        return -1
    else:
        return 0


# 找temp中第一个满足条件的下标
def find_specific(TYPE, temp, my_path):
    my_df = pd.read_csv(my_path)
    my_list = my_df.loc[:, "word"].tolist()
    del my_df
    if TYPE == SBV:
        for sub_temp, pre_temp in temp.sbv:
            if temp.words[sub_temp] in my_list:
                return sub_temp
    elif TYPE == HED:
        for hed_temp, pre_temp in temp.hed:
            if temp.words[hed_temp] in my_list:
                return hed_temp

    return -1


def exam_check(obj, pos_path, neg_path, deny_path, exam_path, self_path): # exam_path 就是 主体的路径

    temp = obj
    # print(temp.words)
    flag = True
    tot_emo = 1
    for word in temp.words:
        if is_in(word, exam_path) == 1:
            flag = False
            for emo in temp.words:
                if is_in(emo, neg_path) == 1:
                    tot_emo = -1
                    break
            break
    for word in temp.words:
        if is_in(word, deny_path) == 1:
            tot_emo = tot_emo * (-1)
    if flag:   # 压根没有考试
        return 0
    # print(tot_emo)
    flag = False
    attr_dict = []
    for atr in temp.attr_dict_list:
        flag = True
        attr_dict = atr
        break
    if flag:
        sign_sub(attr_dict["subject"])  # 主语是我，宾语是学业/学业
        sign_obj_predicate(attr_dict["predicate"], neg_path)  # 消极存在是1

    exam_sub_id = find_specific(SBV, temp, exam_path)

    if exam_sub_id == -1:

        # 考砸了 ,先找 HED里有没有考，有的话直接找CMP(砸，考)||COO(za,kao)，和ADV(MEI,考)
        hed_id = find_specific(HED, temp, exam_path)
        pre_deny = -1
        if hed_id == -1:
            pass
        else:  # 考砸了
            adv_id = find_index(ADV, temp, hed_id)  # 没 考
            if len(adv_id) == 0:  # 考
                pass
            else:   # 没 考
                for temp_deny in adv_id:
                    if judge_adv_deny(temp.words[temp_deny], deny_path):
                        pre_deny = pre_deny * (-1)
            pre_id = find_index(CMP, temp, hed_id)
            if len(pre_id) == 0:  # 考。
                # 找COO
                coo_id = find_index(COO, temp, hed_id)
                if len(coo_id) == 0:
                    tmp = judge_neg_pos(temp.words[hed_id], neg_path, pos_path)
                    if tmp == -1 and pre_deny == -1:    # 
                        return -1
                    elif tmp == -1 and pre_deny == 1:   # 
                        return 1
                    elif tmp == 1 and pre_deny == -1:   # 
                        return 1
                    elif tmp == 1 and pre_deny == 1:    # 
                        return -1
                    else:
                        return tot_emo
                else:
                    pre_id = coo_id
            pre_emotion = judge_neg_pos(temp.words[pre_id[0]], neg_path, pos_path)
            if pre_emotion == 1 and pre_deny == -1:   # 考好
                return 1
            elif pre_emotion == 1 and pre_deny == 1:  # 没考好
                return -1
            elif pre_emotion == -1 and pre_deny == -1: # 考砸
                return -1
            elif pre_emotion == -1 and pre_deny == 1:  # 没考砸
                return 1
            else:
                return tot_emo



    else:  # 我（不）（觉得）考试（不）难
        # if attr_dict["subject"][1] == 4:    # 考试难，考试没过
        pre_id = find_index(SBV, temp, exam_sub_id)  # 得到难/考
        adv_id = find_index(ADV, temp, pre_id[0])
        cmp_id = find_index(CMP, temp, pre_id[0]) # 考试没考好 的 好
        cmp_emo = 0
        if len(cmp_id) == 0:
            pass
        else:
            cmp_emo = judge_neg_pos(temp.words[cmp_id[0]], neg_path, pos_path)
        # 判断pre_id极性
        if len(pre_id) == 0:
            return tot_emo
        pre_emo = judge_neg_pos(temp.words[pre_id[0]], neg_path, pos_path)
        pre_deny = -1
        if len(adv_id) == 0:  # 不存在adv
            pre_deny = -1
        else:  # 追溯所有的否定前缀
            for temp_deny in adv_id:
                # (temp.words[temp_deny])
                if judge_adv_deny(temp.words[temp_deny], deny_path):
                    pre_deny = pre_deny * (-1)

        # 有 我 觉得
        if attr_dict["subject"][1] == 1:
            me_id = find_specific(SBV, temp, self_path)
            if me_id == -1:
                pass
            else:
                pre_id = find_index(SBV, temp, me_id)  # 觉得
                if len(pre_id) == 0:    # 考试 难
                    pass
                else:
                    adv_id = find_index(ADV, temp, pre_id[0])  # 不！觉得
                    if len(adv_id) == 0:  # 不存在adv  我觉得 考试难
                        pass
                    else:   # 我 （）觉得考试难
                        for temp_deny in adv_id:
                            if judge_adv_deny(temp.words[temp_deny], deny_path):
                                pre_deny = pre_deny * (-1)


        if pre_emo == -1 and pre_deny == -1:  # 难
            return -1
        elif pre_emo == -1 and pre_deny == 1:  # 不难
            return 1
        elif pre_emo == 1 and pre_deny == -1:  # 简单
            return 1
        elif pre_emo == 1 and pre_deny == 1:  # 不简单
            return -1
        else:   # 一般
            if pre_emo == 0:
                if pre_deny == 1 and cmp_emo == 1:  # 
                    return -1
                elif pre_deny == -1 and cmp_emo == 1:  #
                    return 1
                elif pre_deny == 1 and cmp_emo == -1:  #
                    return 1
                elif pre_deny == -1 and cmp_emo == -1:  #
                    return -1
            return tot_emo
    return tot_emo
    # 我觉得 考试难
    # 判断 SBV(考试存不存在)


# 基本上能判断好和差
# 但是要根据：考试
def exam_txt(obj):
    direct_pos_path = 'dict/special_judge/exam/direct_pos.csv'
    pos_path = 'dict/special_judge/exam/exam_pos.csv'
    neg_path = 'dict/special_judge/exam/exam_neg.csv'
    deny_path = 'dict/special_judge/exam/exam_deny.csv'
    exam_path = 'dict/special_judge/exam/exam.csv'
    self_path = 'dict/subject/self.csv'

    res = exam_check(obj, pos_path, neg_path, deny_path, exam_path, self_path)

    if '要高考' in obj.seq:
        return "加油，我看好你"
    # print(res)
    msg = jieba.lcut(obj.seq)
    # print(msg)
    for word in msg:
        if word == '好难' and res !=0:
            res = -1
            break
    flag_cheat = False
    # 判断作弊倾向
    for word in msg:
        if word == '作弊':
            flag_cheat = True
            break
    if flag_cheat is True:
        response = ['作弊是不好的行为啦',
                    '做事要讲究原则啦'
                    '不去努力一下，怎么知道到底行不行呢',
                    '学习差什么的都不重要，最重要的是诚信',
                    '我觉得作弊不好',
                    '与其在这里讨论，不如多去看看书呢']
        return random.choice(response)

    # 没考试
    if res == 0:
        return 0

    # 担心考试
    flag_worry = False
    for word in msg:
        if word == '担心' or word == '害怕' or word == '怕' or word == '愁' or word == '担忧':
            flag_worry = True
            break
    if flag_worry is True:
        response = ['我相信你，你也要相信自己哦',
                    '我相信你！',
                    '你可以的~',
                    '无论好坏，认真考了，就不辜负自己的努力',
                    '不是所有人都擅长考试的，不要泄气哦',
                    '给你打气！噗噗噗噗~加油加油',
                    '如果很紧张很担心的话，就去听点歌或者做点别的转移注意力吧',
                    '来，本姑娘赐你"逢考必过","想考几分就考几分"符，包你过！嘿嘿',
                    '嗯？我相信你！',
                    '最后的结果不重要，过程才是关键',
                    '不担心不担心~',
                    '走，看书复习去~',
                    '要不咱们再去复习复习？']
        return random.choice(response)

    flag_score = False
    # 判断是不是再讲成绩
    for word in msg:
        if word == '成绩' or word == '分数':
            flag_score = True
            break
    if flag_score is True:
        if "糟" in obj.seq:
            res = -1
        if res == 1:  # 成绩好
            response = ['可以去吃一顿大餐啦',
                        '想好怎么奖励自己了吗？',
                        '嘻嘻，恭喜你哦',
                        '哇，那我也替你开心，甚至想唱首歌给你听',
                        '干的漂亮！奖励你啥好呢……一个香吻=3=',
                        'Nice！',
                        '棒棒哒~',
                        '夸夸你嘿嘿',
                        '炸鸡披萨奶茶冰淇淋火锅安排一下？消遣消遣']
            return random.choice(response)
        else:     # 成绩不好/一般
            response = ['加油~再接再厉',
                        '我看好你哦',
                        '我以前考试的时候，考的不好就想下次一定要更好',
                        '这次不理想没关系呀，我们还有下次呢',
                        '好好复习，下次一定会考好的',
                        '调整一下状态，不要让短暂的失意阻碍你的前行哦',
                        '呜呜呜我也不喜欢考试',
                        '成绩算啥，分数算啥，你才是我心中最重要的存在~',
                        '嘘……就让往事随风~都随风~',
                        '加油加油！加油加油~',
                        '不要失去信心哦',
                        '考的不理想就多看看没准备好的地方~',
                        '查漏补缺，下次一定行！'
                        '呔~我画个圈圈祝福你逢考必过、考的都会！']
            return random.choice(response)
    if "糟" in obj.seq:
        res = -1
    if res == 1:
        response = ['我知道你可以的~',
                    '看来是清华北大的苗子呀哈哈哈',
                    '可以去吃一顿大餐啦',
                    '想好怎么奖励自己了吗？',
                    '嘻嘻，恭喜你哦',
                    '哇，那我也替你开心，甚至想唱首歌给你听',
                    '干的漂亮！奖励你啥好呢……一个香吻=3=',
                    'Nice！',
                    '棒棒哒~',
                    '夸夸你嘿嘿',
                    '炸鸡披萨奶茶冰淇淋火锅安排一下？消遣消遣',
                    '加油加油~',
                    '我觉得你超厉害的！']
        return random.choice(response)

    else:
        response = ['加油~再接再厉',
                    '我看好你哦',
                    '我以前考试的时候，考的不好就想下次一定要更好',
                    '这次不理想没关系呀，我们还有下次呢',
                    '好好复习，下次一定会考好的',
                    '调整一下状态，不要让短暂的失意阻碍你的前行哦',
                    '呜呜呜我也不喜欢考试',
                    '成绩算啥，分数算啥，你才是我心中最重要的存在~',
                    '嘘……就让往事随风~都随风~',
                    '加油加油！加油加油~',
                    '不要失去信心哦',                        
                    '呔~我画个圈圈祝福你以后逢考必过、考的都会！妈咪妈咪哄~',
                    '没关系，一次失败不代表什么']
        return random.choice(response)



if __name__ == "__main__":
    while 1:
        print("输入：")
        msg = input()
        if msg == 'exit':
            break
        print("结束.")