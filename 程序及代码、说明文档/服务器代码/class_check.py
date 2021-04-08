from analyze_attr import get_qgxs
from data_process import analysis_sentence
import pandas as pd
import random
from analyze_attr import clean_zh_text
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
BAD = "1"

def seek_adv_deny(adv_list, deny_path):
    deny_df = pd.read_csv(deny_path)
    deny_list = deny_df.loc[:, 'word'].tolist()
    del deny_df

    ans = 1
    for word_adv in adv_list[0]:
        if word_adv in deny_list:
            ans = ans * (-1)

    return adv_list[1]


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


# 判断 id 的 adv 是不是否定，否定为-1
def judge_seek_adv_deny(word_id, obj, deny_path):
    index = find_index(ADV, obj, word_id)
    flag = 1
    for id in index:
        if is_in(obj.words[id], deny_path) == 1:
           flag = flag * (-1)
    return flag


# 第一个符合word的id , -1没找到 下标从0开始
def trans_word_to_id(word, obj):
    cnt = 0
    for w in obj.words:
        if w == word:
            return cnt
        cnt = cnt + 1
    return -1


def entity_check(obj, pos_path, neg_path, deny_path, entity_path, self_path): # class_path 就是 主体的路径

    temp = obj
    # print(temp.words)
    flag = True
    tot_emo = 1
    for word in temp.words:
        if is_in(word, entity_path) == 1:
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

    entity_sub_id = find_specific(SBV, temp, entity_path)

    if entity_sub_id == -1:

        # 考砸了 ,先找 HED里有没有考，有的话直接找CMP(砸，考) adv(?,砸)||COO(za,kao)，和ADV(MEI,考)
        hed_id = find_specific(HED, temp, entity_path)
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
            # 新增 考试 “不” 专心
            adv2_id = find_index(ADV, temp, pre_id[0])
            for temp_deny in adv2_id:
                if judge_adv_deny(temp.words[temp_deny], deny_path):
                    pre_deny = pre_deny * (-1)

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
        pre_id = find_index(SBV, temp, entity_sub_id)  # 得到难/考
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
                # print(temp.words[temp_deny])
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
# 上课
def class_txt(obj):
    direct_pos_path = 'dict/special_judge/class/direct_pos.csv'
    pos_path = 'dict/special_judge/class/class_pos.csv'
    neg_path = 'dict/special_judge/class/class_neg.csv'
    deny_path = 'dict/special_judge/class/class_deny.csv'
    class_path = 'dict/special_judge/class/class.csv'
    self_path = 'dict/subject/self.csv'

    if "学习" in obj.seq:
        if "学不进" in obj.seq or "学不好" in obj.seq:
            return random.choice(['可以选择换个学习方式，比如可以尝试和别人交流'])
        else:
            return random.choice(['加油~'])
    res = entity_check(obj, pos_path, neg_path, deny_path, class_path, self_path)

    # print(res)
    if res == 0:
        return 0
    msg = jieba.lcut(obj.seq)
    print(msg)
    for word in msg:
        if word == '好难':
            res = -1
            break

    # 上课睡觉
    flag_sleep = False
    for word in msg:
        if word == '睡觉' or word == '睡着' or word == '困' or word == '昏昏欲睡' or word == '睡':
            flag_sleep = True
            break
    if flag_sleep is True:
        response = ['趁人不注意和周公下棋去了？哈哈',
                    '我有次上课看着老师就睡着了，太尴尬了',
                    '你是晚上没睡好么？',
                    '当代学生现状，哈哈',
                    '只要你课后能把上课讲的弄懂就好',
                    '老师没发现你？',
                    '我也是，我上物理课老睡着',
                    '哎，老师也很无奈~',
                    '你呀~',
                    '打起精神来~',
                    '想起一张图片，你可以把眼睛画眼皮上(手动滑稽)',
                    '上课睡觉最大的坏处就是……睡的不舒服~',
                    '该听的课还是要听嘛']
        return random.choice(response)

    # 上课不专心
    flag_concentrate = False
    for word in msg:
        if word in ['开小差', '专心', '注意力']:
            flag_concentrate = True
            break
    if flag_concentrate is True:
        if res == -1:
            response = ['要专心一点',
                        '打起精神来~',
                        '不听课就要课后去补呢',
                        '哎，真是无奈',
                        '身在曹营心在汉么',
                        '说，是不是因为在想我？',
                        '我也不懂，要不问问老师去',
                        '好好听课吧']
            return random.choice(response)

    # 听得懂，专心
    if res == -1:
        response = ['你认真起来谁都挡不住',
                    '冲冲冲！',
                    '我看好你~',
                    '哎呀认真起来的你会发光捏！',
                    '你这么聪明肯定能懂~',
                    '过来人的经验：上课多听讲，下课就能省点心',
                    '芝士(划掉)知识就是力量！'
                    '哈哈哈，老师看了都想夸你']
        return random.choice(response)

    # 听不懂
    elif res == 1:
        response = ['没事儿，多去问问老师',
                    '那句话叫啥来着，人非圣贤，孰能无惑，对吧',
                    '我还在念书的时候，也总听不懂。不懂就问哦'
                    '可以向老师同学虚心讨教',
                    '加油哦~',
                    '我相信你可以的！',
                    '学它！',
                    '读书是难，可不用担心别的，一股脑儿冲就行']
    return random.choice(response)


def homework_txt(obj):
    direct_pos_path = 'dict/special_judge/homework/direct_pos.csv'
    pos_path = 'dict/special_judge/homework/homework_pos.csv'
    neg_path = 'dict/special_judge/homework/homework_neg.csv'
    deny_path = 'dict/special_judge/homework/homework_deny.csv'
    homework_path = 'dict/special_judge/homework/homework.csv'
    self_path = 'dict/subject/self.csv'

    res = entity_check(obj, pos_path, neg_path, deny_path, homework_path, self_path)
    if "不想上学" in obj.seq:
        return random.choice(['乖啦，要不先干点别的'])
    # print(res)
    if res == 0:
        return 0
    msg = jieba.lcut(obj.seq)
    print(msg)
    for word in msg:
        if word == '好难':
            res = -1
            break

    # 抄作业
    flag_copy = False
    for word in msg:
        if word in ['抄袭']:
            flag_copy = True
            break
    if flag_copy is True:
        response = ['我觉得吧，抄袭是可耻的行为',
                    '哎，抄袭让人失去原则',
                    '不好去抄袭的啦',
                    '自己去完成不好么',
                    '我不赞成这样的行为……']
        return random.choice(response)

    if res == -1:
        response = ['哎，可怜的孩子~',
                    '加油，我看好你哦',
                    '要不要先休息一下？',
                    '俺做作业的时候喜欢听歌，这样就是满满的动力~',
                    '老弟，来一首黑怕(hip-pop)，提提精神咋样',
                    '自己的功课，咋样也要完成',
                    '我给你当拉拉队，加油加油(^ω^)',
                    '咱别看手机了，看书吧Orz',
                    '咱可以场外求助不？问问同学老师',
                    '冲呀~',
                    '我表示我也很头疼这个……']
        return random.choice(response)
    elif res == 1:
        response = ['嘿嘿，不愧是你~',
                    '没有啥能难倒你的，小朋友',
                    '真行~',
                    '看你这么辛苦，来杯奶茶放松一下不？',
                    '埋头就是干',
                    '没有咱完不成的任务~',
                    '那你要不要帮我也把代码写了？（做梦ing）']
        return random.choice(response)
    return 0


# 项目
def project_txt(obj):
    direct_pos_path = 'dict/special_judge/project/direct_pos.csv'
    pos_path = 'dict/special_judge/project/project_pos.csv'
    neg_path = 'dict/special_judge/project/project_neg.csv'
    deny_path = 'dict/special_judge/project/project_deny.csv'
    project_path = 'dict/special_judge/project/project.csv'
    self_path = 'dict/subject/self.csv'

    res = entity_check(obj, pos_path, neg_path, deny_path, project_path, self_path)

    # print(res)
    if res == 0:
        return 0
    msg = jieba.lcut(obj.seq)
    print(msg)
    for word in msg:
        if word == '好难':
            res = -1
            break

    # 抄
    flag_copy = False
    for word in msg:
        if word in ['抄袭']:
            flag_copy = True
            break
    if flag_copy is True:
        response = ['我觉得吧，抄袭是可耻的行为',
                    '哎，抄袭让人失去原则',
                    '不好去抄袭的啦',
                    '自己去完成不好么',
                    '我不赞成这样的行为……']
        return random.choice(response)

    if res == -1:
        response = ['哎，可怜的孩子~',
                    '加油，我看好你哦',
                    '要不要先休息一下？',
                    '好的项目需要精雕细琢',
                    '就是因为有困难才要上嘛',
                    '自己的项目，咋样也要完成',
                    '我给你当拉拉队，加油加油(^ω^)',
                    '每个项目都有这样的过程',
                    '咱可以场外求助不？问问同学老师',
                    '冲呀~',
                    '我表示我也很头疼这个……']
        return random.choice(response)
    elif res == 1:
        response = ['嘿嘿，不愧是你~',
                    '没有啥能难倒你的，小朋友',
                    '真行~',
                    '看你这么辛苦，来杯奶茶放松一下不？',
                    '埋头就是干',
                    '没有咱完不成的任务~',
                    '那你要不要帮我也把代码写了？（做梦ing）']
        return random.choice(response)
    return 0


# 毕设
def design_txt(obj):
    direct_pos_path = 'dict/special_judge/project/direct_pos.csv'
    pos_path = 'dict/special_judge/design/design_pos.csv'
    neg_path = 'dict/special_judge/design/design_neg.csv'
    deny_path = 'dict/special_judge/design/design_deny.csv'
    design_path = 'dict/special_judge/design/design.csv'
    self_path = 'dict/subject/self.csv'

    res = entity_check(obj, pos_path, neg_path, deny_path, design_path, self_path)

    # print(res)
    if res == 0:
        return 0
    msg = jieba.lcut(obj.seq)
    print(msg)
    for word in msg:
        if word == '好难':
            res = -1
            break
    ##
    if res == -1:
        response = ['哎，可怜的孩子~',
                    '加油，我看好你哦',
                    '要不要先休息一下？',
                    '好的毕设需要精雕细琢',
                    '就是因为有困难才要上嘛',
                    '自己的毕设，咋样也要完成',
                    '我给你当拉拉队，加油加油(^ω^)',
                    '每个毕设都有这样的过程',
                    '咱可以场外求助不？问问同学老师',
                    '冲呀~',
                    '我表示我也很头疼这个……']
        return random.choice(response)
    elif res == 1:
        response = ['没有啥能难倒你的，小朋友',
                    '看你这么辛苦，来杯奶茶放松一下不？',
                    '埋头就是干',
                    '没有咱完不成的毕设~',
                    '那你要不要帮我也把代码写了？（做梦ing）']
        return random.choice(response)
    return 0

# 天气
def weather_txt(obj, mood):
    direct_pos_path = 'dict/special_judge/project/direct_pos.csv'
    weather_path = 'dict/special_judge/weather/weather.csv'
    sunny_path = 'dict/special_judge/weather/sunny.csv'
    rainy_path = 'dict/special_judge/weather/rainy.csv'
    snowy_path = 'dict/special_judge/weather/snowy.csv'
    windy_path = 'dict/special_judge/weather/windy.csv'
    cloudy_path = 'dict/special_judge/weather/cloudy.csv'
    deny_path = 'dict/special_judge/design/design_deny.csv'

    if "阴天" in obj.seq:
        if "让我" in obj.seq:
            return random.choice(['太阳一定会出现的'])
        return random.choice(['那是太阳在和你玩捉迷藏'])
    # 大判断
    weather_flag = False
    for word in obj.words:
        if is_in(word, weather_path) == 1:
            weather_flag = True
            break
    if weather_flag is False:
        return 0

    # 晴天
    cnt = 0
    for word in obj.words:
        if is_in(word, sunny_path) == 1:
            if judge_seek_adv_deny(cnt, obj, deny_path) == -1:
                break
            response = ['天气好，心情也好~',
                        '太阳当空照，花儿对你笑',
                        '我很喜欢晴天',
                        '阳光什么最喜欢啦',
                        '天气这么好，咱出去玩吗',
                        '啊~太阳',
                        '洗衣服的好日子',
                        '哈哈，今日宜晒被子',
                        '要是能泡杯茶，躺在阳光下……巴适~',
                        '是啊是啊',
                        '那你今天准备干嘛？',
                        '今天打算做啥？']
            return random.choice(response)
        cnt = cnt + 1

    # 雨天
    cnt = 0
    for word in obj.words:
        if is_in(word, rainy_path) == 1:
            if judge_seek_adv_deny(cnt, obj, deny_path) == -1:
                break
            response = ['又下雨了嘛',
                        '那今天打算做啥？',
                        '不喜欢下雨天出门，湿湿的',
                        '下雨天我比较喜欢躲在家里',
                        '那你还出门吗',
                        '出门记得带伞呀',
                        '小心别感冒了',
                        '啊哦，小心淋雨',
                        '天公不作美啊',
                        '我老家浙江经常下雨，梅雨季节更加了……']
            return random.choice(response)
        cnt = cnt + 1

    # 彩虹
    cnt = 0
    for word in obj.words:
        if word == '彩虹':
            if judge_seek_adv_deny(cnt, obj, deny_path) == -1:
                break
            response = ['哇~',
                        '哇塞，羡慕！',
                        '我不怎么看见过彩虹诶',
                        '哇，那你拍照了吗？',
                        '说明你今天有好运气哦',
                        '美丽的彩虹~',
                        '好棒啊',
                        '我也想看彩虹']
            return random.choice(response)
        cnt = cnt + 1

    # 冰雹
    cnt = 0
    for word in obj.words:
        if word == '冰雹':
            if judge_seek_adv_deny(cnt, obj, deny_path) == -1:
                break
            response = ['哇~',
                        '我没见过冰雹诶……',
                        '冰雹……大吗？',
                        '上一次下冰雹的时候，我还在家里睡大觉',
                        '没砸着你吧',
                        '天哪，严不严重啊',
                        '出门当心哦']
            return random.choice(response)
        cnt = cnt + 1

    # 下雪
    cnt = 0
    for word in obj.words:
        if is_in(word, snowy_path) == 1:
            if judge_seek_adv_deny(cnt, obj, deny_path) == -1:
                break
            response = ['哇，下雪了！',
                        '那今天打算做啥？',
                        '走走走，堆雪人去~',
                        '南方不常见大雪~想去北方耍耍'
                        '那你还出门吗',
                        '出门记得带伞呀',
                        '小心别感冒了',
                        '打雪仗！',
                        '下雪天开车有点危险哦',
                        '出门当心脚下哦',
                        '上次下大雪，我摔了两个屁股蹲！',
                        '雪花飘飘~北风萧萧~',
                        '再过一会就变成银装素裹的世界啦',
                        '呼呼，喜欢下雪天']
            return random.choice(response)
        cnt = cnt + 1

    # 多云
    cnt = 0
    for word in obj.words:
        if is_in(word, cloudy_path) == 1:
            if judge_seek_adv_deny(cnt, obj, deny_path) == -1:
                break
            response = ['赶快出太阳吧~',
                        '多云天有一种闷闷的味道',
                        '多云天总感觉很暗呢',
                        '哦~乌云乌云快走开']
            return random.choice(response)
        cnt = cnt + 1

    # 大风
    cnt = 0
    for word in obj.words:
        if is_in(word, cloudy_path) == 1:
            if judge_seek_adv_deny(cnt, obj, deny_path) == -1:
                break
            response = ['凉飕飕的……',
                        '吹呀吹呀我的骄傲放纵~',
                        '呼呼呼，躲在被窝里瑟瑟发抖']
            return random.choice(response)
        cnt = cnt + 1

    # 其他
    bad = ['差', '糟糕', '坏', '不好', '不舒服', '阴沉']
    for word in bad:
        if word in obj.seq:
            if mood == BAD:
                return random.choice(['天气好的话，心情也会好一些呢',
                                      '对呀，不过天气总会好起来的',
                                      '没关系，老天也总有眉开眼笑的时候。'])
            else:
                return random.choice(['希望天气好一点~',
                                      '天气好的话，心情也会好一些呢',
                                      '但这不是人力可以改变的',
                                      '这天气是挺不舒服的',
                                      '我也希望天气能够好一点'])
    response = ['希望天气好一点~',
                '你比较喜欢什么样的天气？',
                '比起下雨，我还是喜欢晴天的样子',
                '天气总是能影响人们的心情……',
                '天气好的话，心情也会好一些呢']
    return random.choice(response)


# 父母吵架问题
def parent_txt(obj):
    deny_path = 'dict/special_judge/parent/deny.csv'
    parent_path = 'dict/special_judge/parent/parent.csv'
    fight_path = 'dict/special_judge/parent/fight.csv'
    self_path = 'dict/subject/self.csv'
    happy_path = 'dict/special_judge/parent/happy.csv'

    res = entity_check(obj, happy_path, fight_path, deny_path, parent_path, self_path)
    if "离婚" in obj.seq or "离异" in obj.seq:
        return random.choice(['我的父母也离婚了',
                              '说真的，不幸的婚姻就是悲剧',
                              '与其天天吵架，不如早点离婚',
                              '婚姻真成了爱情的坟墓了'])
    if "不理我" in obj.seq:
        if "为什么" in obj.seq:
            return random.choice(['也许应该主动去沟通才好'])
        return random.choice(['可能是太忙了吧'])
    if "不理解" in obj.seq:
        return random.choice(['终归是自己的家人，会好的'])
    if '不爱我' in obj.seq:
        if '妈' in obj.seq:
            return "世上的妈妈怎么会不爱自己的孩子"
    # 有没有写父母
    if res == 0:
        return 0
    if "怎么" in obj.seq or "怎样" in obj.seq or "如何" in obj.seq:
        if "交流" in obj.seq or "沟通" in obj.seq or "相处" in obj.seq:
            return random.choice(['敞开心扉，积极一点'])
    if "不相信" in obj.seq or "不信任" in obj.seq or "不管我" in obj.seq:
        return random.choice(['你还有我',
                              '好好沟通一下吧',
                              '抱抱，他们应该支持你才对'])

    # 负面，这边继续判断是父母之间 还是 我和父母
    if res == -1:
        flag_and = False
        flag_me_and_p = False
        cnt = 0
        for word in obj.words:
            if word == '和':
                flag_and = True
                break
            cnt = cnt + 1

        if flag_and is True:
            if is_in(obj.words[cnt + 1], parent_path) == 1:
                if (cnt-1) < 0:
                    flag_me_and_p = True
                else:
                    if is_in(obj.words[cnt-1], self_path) == 1:
                        flag_me_and_p = True
                    if is_in(obj.words[cnt-1], parent_path) !=1:
                        flag_me_and_p = True
            if is_in(obj.words[cnt + 1], self_path) == 1:
                if (cnt-1) >= 0 and is_in(obj.words[cnt-1], parent_path) == 1:
                    flag_me_and_p = True
                if is_in(obj.words[cnt + 2], parent_path) == 1:
                    if (cnt - 1) < 0:
                        flag_me_and_p = True
                    else:
                        if is_in(obj.words[cnt - 1], self_path) == 1:
                            flag_me_and_p = True

        # 父母自己吵架
        if flag_me_and_p is False:
            response = ['啊……哎……心疼你',
                        '哎，我曾经也来自这样的家庭',
                        '所以说，不幸的家庭各有各的不幸啊……',
                        '很想安慰你，可惜我能做的也有限',
                        '还能怎么办，我们只能当中间和好的那座桥梁。',
                        '你也很难受吧，不要担心，会好的',
                        '去听听《不透气的房间》吧，那里有所有我对你的感同身受',
                        '抱抱你，希望天下再也没有一样受伤的家庭',
                        '好难，好难……']
            return random.choice(response)

        # 我和父母吵架
        else:
            response = ['唉，抱抱，不管怎么样他们还是你的家人',
                        '不气不气',
                        '过两天气消了就好了',
                        '发生了啥',
                        '你们怎么了',
                        '和家人吵架是难免的，毕竟两代人的观念都不一样',
                        '出什么事情了吗？',
                        '吵过就算了，不要太放在心上']
            return random.choice(response)

    else:
        response = ['父母也挺不容易的',
                    '不管发生什么他们总是站在我们身后',
                    '你要相信你是幸福的',
                    '父母应该是最关心我们的']
        return random.choice(response)
    return 0


# 同学
def classmate_txt(obj):
    deny_path = 'dict/special_judge/classmate/deny.csv'
    classmate_path = 'dict/special_judge/classmate/classmate.csv'
    fight_path = 'dict/special_judge/classmate/fight.csv'
    self_path = 'dict/subject/self.csv'
    happy_path = 'dict/special_judge/classmate/happy.csv'
    bulin_path = 'dict/special_judge/classmate/bulin.csv'

    res = entity_check(obj, happy_path, fight_path, deny_path, classmate_path, self_path)
    alone = ["没有朋友", "没朋友"]
    for word in alone:
        if word in obj.seq:
            return random.choice(["不是的，在你需要的时候，随时可以找他们",'我会是你最忠实的朋友'])
    if "没" in obj.seq and "朋友" in obj.seq:
        return random.choice(['我会是你最忠实的朋友',"不是的，在你需要的时候，随时可以找他们"])
    if "你会" in obj.seq and "孤独" in obj.seq:
        return random.choice(['我不是一个人，我还有你呀'])
    alone = ['孤单', '孤独','只有自己']
    for word in alone:
        if word in obj.seq:
            return random.choice(["你有很多朋友的，可能只是你没发现",'你还有我','不管怎么样，我永远陪着你'])
    if "有一个人" in obj.seq:
        return random.choice(['是吗'])
    if "对我" in obj.seq:
        if "不好" in obj.seq:
            return random.choice(['为什么呀'])
        if "凶" in obj.seq:
            return random.choice(['也许他是另一种保护你的方式'])
    if "一个人" in obj.seq:
        if "静" in obj.seq:
            return random.choice(['也好'])
        if '怕' in obj.seq:
            return random.choice(['要战胜自己，有我陪你'])
        return random.choice(['人于这个世界，是以集体为单位的'])
    if "多个人" in obj.seq:
        return random.choice(['大家在一起才能交到朋友'])
    if "怎么" in obj.seq or "怎样" in obj.seq or "如何" in obj.seq:
        if "交流" in obj.seq or "沟通" in obj.seq or "相处" in obj.seq:
            return random.choice(['敞开心扉，积极一点'])
    # 有没有写
    if res == 0:
        return 0
    # 负面，这边继续判断是同学之间 还是 我和同学
    if res == -1:
        flag_and = False
        flag_me_and_p = False
        cnt = 0
        for word in obj.words:
            if word == '和':
                flag_and = True
                break
            cnt = cnt + 1

        if flag_and is True:
            if is_in(obj.words[cnt + 1], classmate_path) == 1:
                if (cnt-1) < 0:
                    flag_me_and_p = True
                else:
                    if is_in(obj.words[cnt-1], self_path) == 1:
                        flag_me_and_p = True
            if is_in(obj.words[cnt + 1], self_path) == 1:
                if (cnt-1) >= 0 and is_in(obj.words[cnt-1], classmate_path) == 1:
                    flag_me_and_p = True
                if is_in(obj.words[cnt + 2], classmate_path) == 1:
                    if (cnt - 1) < 0:
                        flag_me_and_p = True
                    else:
                        if is_in(obj.words[cnt - 1], self_path) == 1:
                            flag_me_and_p = True
        if "我被" in obj.seq or "把我" in obj.seq or "我跟" in obj.seq or "跟我" in obj.seq or "我和" in obj.seq or "和我" in obj.seq \
                or "和同学" in obj.seq:
            flag_me_and_p = True

        # 同学之间吵架
        if flag_me_and_p is False:
            # 判断是不是校园霸凌
            flag_bulin = False
            for word in obj.words:
                if is_in(word, bulin_path) == 1:
                    flag_bulin = True
                    break
            if flag_bulin is False:
                response = ['啊……那要不去安慰他们？',
                            '那你打算怎么办啊？',
                            '大家都是同学，何必呢……',
                            '希望他们能和好吧',
                            '争吵最让人头疼了，哎']
                return random.choice(response)
            else:
                response = ['暴力是不可取的',
                            '再怎么说也不能动手打人',
                            '如果发生了校园霸凌，不管是同学还是自己，一定要告诉学校处理！',
                            '对待暴力，是零容忍的']
                return random.choice(response)

        # 我和同学吵架
        else:
            # 判断是不是校园霸凌
            flag_bulin = False
            for word in obj.words:
                if is_in(word, bulin_path) == 1:
                    flag_bulin = True
                    break
            if flag_bulin is False:
                response = ['唉，抱抱……',
                            '也许过两天就没事了',
                            '发生了啥',
                            '你们怎么了',
                            '毕竟还是同学，朝夕相处的，能不冲突就不冲突吧',
                            '出什么事情了吗？',
                            '可能大家都有问题，还是保持冷静吧',
                            '冲动也是魔鬼，吵架是没必要的']
                return random.choice(response)
            else:
                response = ['暴力是不可取的',
                           '再怎么说也不能动手打人',
                           '如果发生了校园霸凌，不管是同学还是自己，一定要告诉校方处理！',
                           '对待暴力，是零容忍的']
                return random.choice(response)

    return 0


# 室友
def roommate_txt(obj):
    deny_path = 'dict/special_judge/roommate/deny.csv'
    roommate_path = 'dict/special_judge/roommate/roommate.csv'
    fight_path = 'dict/special_judge/roommate/fight.csv'
    self_path = 'dict/subject/self.csv'
    happy_path = 'dict/special_judge/roommate/happy.csv'
    bulin_path = 'dict/special_judge/roommate/bulin.csv'

    res = entity_check(obj, happy_path, fight_path, deny_path, roommate_path, self_path)
    # 有没有写
    if "怎么" in obj.seq or "怎样" in obj.seq or "如何" in obj.seq:
        if "交流" in obj.seq or "沟通" in obj.seq or "相处" in obj.seq:
            return random.choice(['敞开心扉，积极一点'])
    if res == 0:
        return 0

    # 负面，这边继续判断是同学之间 还是 我和同学
    if res == -1:
        flag_and = False
        flag_me_and_p = False
        cnt = 0
        for word in obj.words:
            if word == '和':
                flag_and = True
                break
            cnt = cnt + 1

        if flag_and is True:
            if is_in(obj.words[cnt + 1], roommate_path) == 1:
                if (cnt-1) < 0:
                    flag_me_and_p = True
                else:
                    if is_in(obj.words[cnt-1], self_path) == 1:
                        flag_me_and_p = True
            if is_in(obj.words[cnt + 1], self_path) == 1:
                if (cnt-1) >= 0 and is_in(obj.words[cnt-1], roommate_path) == 1:
                    flag_me_and_p = True
                if is_in(obj.words[cnt + 2], roommate_path) == 1:
                    if (cnt - 1) < 0:
                        flag_me_and_p = True
                    else:
                        if is_in(obj.words[cnt - 1], self_path) == 1:
                            flag_me_and_p = True

        # 同学之间吵架
        if flag_me_and_p is False:
            # 判断是不是校园霸凌
            flag_bulin = False
            for word in obj.words:
                if is_in(word, bulin_path) == 1:
                    flag_bulin = True
                    break
            if flag_bulin is False:
                response = ['啊……那要不去安慰他们？',
                            '那你打算怎么办啊？',
                            '大家都是室友，何必呢……',
                            '希望他们能和好吧',
                            '争吵最让人头疼了，哎']
                return random.choice(response)
            else:
                response = ['暴力是不可取的',
                            '再怎么说也不能动手打人',
                            '如果发生了校园霸凌，不管是同学还是自己，一定要告诉校方处理！',
                            '对待暴力，是零容忍的']
                return random.choice(response)

        # 我和同学吵架
        else:
            # 判断是不是校园霸凌
            flag_bulin = False
            for word in obj.words:
                if is_in(word, bulin_path) == 1:
                    flag_bulin = True
                    break
            if flag_bulin is False:
                response = ['唉，抱抱……',
                            '也许过两天就没事了',
                            '发生了啥',
                            '你们怎么了',
                            '毕竟还是室友，朝夕相处的，能不冲突就不冲突吧',
                            '出什么事情了吗？',
                            '可能大家都有问题，还是保持冷静吧',
                            '冲动也是魔鬼，吵架是没必要的']
                return random.choice(response)
            else:
                response = ['暴力是不可取的',
                           '再怎么说也不能动手打人',
                           '如果发生了校园霸凌，不管是同学还是自己，一定要告诉校方处理！',
                           '对待暴力，是零容忍的']
                return random.choice(response)
    return 0


# 朋友 缺 我没有朋友
def friend_txt(obj):
    friend_path = 'dict/special_judge/friend/friend.csv'
    fight_path = 'dict/special_judge/friend/fight.csv'
    self_path = 'dict/subject/self.csv'
    deny_path = 'dict/special_judge/friend/deny.csv'
    happy_path = 'dict/special_judge/friend/happy.csv'
    bulin_path = 'dict/special_judge/friend/bulin.csv'
    less_path = 'dict/special_judge/friend/less.csv'

    res = entity_check(obj, happy_path, fight_path, deny_path, friend_path, self_path)
    if "朋友" in obj.seq:
        res = 0
        if "少" in obj.seq:
            return random.choice(['我会一直陪在你身边的'])
        if "想有" in obj.seq:
            return random.choice(['朋友是要真诚对待的呢','会有的','多和别人交流，会有的'])
        if "挺好" in obj.seq:
            return random.choice(['有朋友就是好'])
        if "不喜欢" in obj.seq:
            return random.choice(['可能有什么误会'])
        if "喜欢" in obj.seq:
            return random.choice(['我们会一直陪在你身边的'])
        if "嫌弃我" in obj.seq:
            return random.choice(['怎么会呢'])
        if "一直做" in obj.seq:
            return random.choice(['当然，我会一直陪着你'])
        if "你有" in obj.seq:
            return random.choice(['你就是我的朋友'])
        return random.choice(['朋友是要真诚对待的呢','我永远是你的朋友'])
    # 有没有写
    if res == 0:
        return 0

    # 负面，这边继续判断是同学之间 还是 我和同学
    if res == -1:
        flag_and = False
        flag_me_and_p = False
        cnt = 0
        for word in obj.words:
            if word == '和':
                flag_and = True
                break
            cnt = cnt + 1

        if flag_and is True:
            if is_in(obj.words[cnt + 1], friend_path) == 1:
                if (cnt-1) < 0:
                    flag_me_and_p = True
                else:
                    if is_in(obj.words[cnt-1], self_path) == 1:
                        flag_me_and_p = True
            if is_in(obj.words[cnt + 1], self_path) == 1:
                if (cnt-1) >= 0 and is_in(obj.words[cnt-1], friend_path) == 1:
                    flag_me_and_p = True
                if is_in(obj.words[cnt + 2], friend_path) == 1:
                    if (cnt - 1) < 0:
                        flag_me_and_p = True
                    else:
                        if is_in(obj.words[cnt - 1], self_path) == 1:
                            flag_me_and_p = True

        # 同学之间吵架
        if flag_me_and_p is False:
            # 判断是不是校园霸凌
            flag_bulin = False
            for word in obj.words:
                if is_in(word, bulin_path) == 1:
                    flag_bulin = True
                    break
            if flag_bulin is False:
                response = ['啊……那要不去安慰他们？',
                            '那你打算怎么办啊？',
                            '大家都是朋友，何必呢……',
                            '希望他们能和好吧',
                            '争吵最让人头疼了，哎']
                return random.choice(response)
            else:
                response = ['暴力是不可取的',
                            '再怎么说也不能动手打人',
                            '如果发生了校园霸凌，不管是同学还是自己，一定要告诉校方处理！',
                            '对待暴力，是零容忍的']
                return random.choice(response)

        # 我和同学吵架
        else:
            # 判断是不是校园霸凌
            flag_bulin = False
            for word in obj.words:
                if is_in(word, bulin_path) == 1:
                    flag_bulin = True
                    break
            if flag_bulin is False:
                response = ['唉，抱抱……',
                            '也许过两天就没事了',
                            '发生了啥',
                            '你们怎么了',
                            '毕竟还是朋友，朝夕相处的，能不冲突就不冲突吧',
                            '出什么事情了吗？',
                            '可能大家都有问题，还是保持冷静吧',
                            '冲动也是魔鬼，吵架是没必要的']
                return random.choice(response)
            else:
                response = ['暴力是不可取的',
                           '再怎么说也不能动手打人',
                           '如果发生了校园霸凌，不管是同学还是自己，一定要告诉校方处理！',
                           '对待暴力，是零容忍的']
                return random.choice(response)
    return random.choice(['朋友是要真诚对待的呢'])


# 感情问题
def lover_txt(obj):
    fight_path = 'dict/special_judge/lover/fight.csv'
    lover_path = 'dict/special_judge/lover/lover.csv'
    she_dont_know_path = 'dict/special_judge/lover/she_dont_know.csv'
    broken_path = 'dict/special_judge/lover/broken.csv'
    bulin_path = 'dict/special_judge/lover/bulin.csv'
    tell_path = 'dict/special_judge/lover/tell.csv'
    self_path = 'dict/subject/self.csv'
    deny_path = 'dict/special_judge/lover/deny.csv'
    pos_path = 'dict/special_judge/lover/pos.csv'
    neg_path = 'dict/special_judge/lover/neg.csv'

    # 先判断有没有大的方向
    flag = False
    she_dont_know = False
    if "感情受挫" in obj.seq:
        return random.choice(['抱抱，也许真爱在未来等着你'])
    if "我出轨" in obj.seq:
        return random.choice(['这样会对双方都造成伤害的'])
    if "我绿了" in obj.seq or "被绿" in obj.seq or "绿帽子" in obj.seq or "出轨" in obj.seq or "背叛" in obj.seq:
        return random.choice(['那你应该感谢他帮你认清了一个人','也许没有你想的这么糟糕呢','我也替你很难过，但我听说，“真爱无坦途。”'])
    if "不属于我" in obj.seq:
        if "他" in obj.seq or "她" in obj.seq:
            return random.choice(['不要难过，下一个路口会有更好的风景'])
    q = '爱的人'
    s = '喜欢的人'
    if "爱的人不爱我" in obj.seq or "喜欢的人不喜欢我" in obj.seq:
        return random.choice(['我相信毅力与真情会换来真爱的'])
    if s in obj.seq and "在一起" in obj.seq:
        if "和别人" in obj.seq or "和其他" in obj.seq:
            return random.choice(['你有没有告诉他你的心意','哎，人生有时候就是这样郁闷'])
    cnt = 0
    words = jieba.lcut(obj.seq)
    for w in words:
        if is_in(w, lover_path) == 1:
            flag = True
            break
        if is_in(w, she_dont_know_path) == 1:
            she_dont_know = True
            flag = True
            break
    if obj.seq.count(s) != 0 or obj.seq.count(q)!= 0:
        she_dont_know = True
        flag = True
    flag_tell = False
    flag_broken = False
    if flag is False:
        for w in words:
            if is_in(w, tell_path):
                flag_tell = True
            if is_in(w, broken_path):
                flag_broken = True
        if flag_tell is False and flag_broken is False:
            return 0

    # 在讲暗恋的人
    if she_dont_know is True or flag_tell is True:
        # 告白 成功/失败
        res = entity_check(obj, pos_path , neg_path, deny_path, tell_path, self_path)
        if res == 1:
            response = ['哇哇哇哇，恭喜你！！',
                        '太好了~',
                        '哇，从今以后你也是有对象的人了']
            return random.choice(response)
        elif res == -1:
            response = ['摸摸头，没关系的',
                        '哼，他没有眼光~',
                        '那你要不要改喜欢我？',
                        '人有悲欢离合，月有盈晴圆缺啊']
            return random.choice(response)
        else:  # 讲述
            response = ['有喜欢的人是一件很幸福的事情啦',
                        '他知道你喜欢他吗？',
                        '希望你能够成功攻略他的心',
                        '这就是青春啊……',
                        '他长得好看吗？',
                        '喜欢他让你觉得快乐吗？',
                        '我想起了袁湘琴和江直树，希望你也能找到你的江直树']
            return random.choice(response)

    else:
        # 在讲对象
        # 失恋
        if "不想" in obj.seq:
            return random.choice(['是嘛'])
        if "想有" in obj.seq or '想要' in obj.seq:
            return random.choice(['会有的'])
        for w in words:
            if is_in(w, broken_path):
                flag_broken = True
                break
        if flag_broken is True:
            response = ['哎，抱抱',
                        '世界上这么多人，你一定能找到你的幸福',
                        '失去了你是他的不幸，你值得更好的人',
                        '你一定也不好受吧',
                        '走，咱去找朋友放开了的玩一场！把委屈都释放出来',
                        '可惜我不能当你的对象，不然我一定加倍疼你',
                        '生活会迎来新的起点的']
            return random.choice(response)

        # 吵架
        flag_fight = False
        for w in words:
            if is_in(w, fight_path):
                flag_fight = True
                break
        if flag_fight is True:
            flag_bulin = False
            for w in words:
                if is_in(w, bulin_path):
                    flag_bulin = True
                    break
            # 暴力
            if flag_bulin is True:
                response = ['暴力坚决不能忍啊！',
                            '再怎么样也不能动手',
                            '如果他欺负你了，一定要维护好自己的利益',
                            '抱抱你，如果遇到什么困难，一定要向身边的人求助哦']
                return random.choice(response)
            response = ['哎，抱抱',
                        '大家先冷静下来比较好',
                        '冲动是魔鬼，一定要冷静',
                        '等情绪平复一些，再去沟通吧',
                        '要不要互相换位思考试试呢？',
                        '吵架最难受了',
                        '为了下一次不要再吵架，一定要好好解决两个人之间的问题']
            return random.choice(response)

        else:
            response = ['祝你和你的那位幸福~',
                        '一定要长长久久啊',
                        '来自单身狗的羡慕',
                        '我也想要甜甜的恋爱！',
                        '手牵手，一起走~',
                        '猝不及防的狗粮么……',
                        '有了对象那你还爱我么呜呜呜']
            return random.choice(response)
    return 0


# 老师关系
def teacher_txt(obj):
    teacher_path = 'dict/special_judge/teacher/teacher.csv'
    neg_path = 'dict/special_judge/teacher/neg.csv'
    pos_path = 'dict/special_judge/teacher/pos.csv'
    deny_path = 'dict/special_judge/teacher/deny.csv'

    flag = False
    for w in obj.words:
        if is_in(w, teacher_path):
            flag = True
            break
    if flag is False:
        return 0

    flag_relation = 1
    # 关系不好
    for w in obj.words:
        if is_in(w, neg_path):
            flag_relation = -1
            break
    for w in obj.words:
        if is_in(w, deny_path):
            flag_relation = flag_relation * (-1)

    # 关系好
    if flag_relation == 1:
        response = ['多和老师沟通沟通',
                    '你觉得你有个好老师吗？',
                    '老师对学生的作用还是很重要的',
                    '和好老师一起相处，学习都轻松了不少']
        return random.choice(response)
    # 关系不好
    elif flag_relation == -1:
        response = ['多和老师沟通沟通',
                    '你觉得你有个好老师吗？',
                    '老师对学生的作用还是很重要的']
        return random.choice(response)
    return 0


# 社交恐惧
def social_txt(obj):
    social_path = 'dict/special_judge/social/social.csv'
    neg_path = 'dict/special_judge/social/neg.csv'
    pos_path = 'dict/special_judge/social/pos.csv'
    deny_path = 'dict/special_judge/social/deny.csv'

    communicate = ['交流','沟通','对话','说话','讲话']
    for word in communicate:
        if word in obj.seq:
            if "不想" in obj.seq or "没有兴趣" in obj.seq or "没兴趣" in obj.seq or "不感兴趣" in obj.seq or "没意思" in obj.seq or "没什么兴趣" in obj.seq or '不喜欢' in obj.seq or "不爱" in obj.seq:
                return random.choice(['要多和别人交流','尝试与别人交流，你会发现新世界','多与别人沟通，你会发现生活的美'])
            if '难' in obj.seq:
                return random.choice(['要有勇气再去尝试'])
            if "怎么" in obj.seq or "不会" in obj.seq:
                return random.choice(['礼貌一点，积极一点','按自己想法慢慢说','多练练就好了'])
            if "不敢" in obj.seq or "怕" in obj.seq:
                return random.choice(['大家会善待你的，不会伤害你'])
            if "不太爱" in obj.seq or "不爱" in obj.seq:
                return random.choice(['交流很重要'])
            if '跟谁' in obj.seq:
                return "和我呀"
    if '社会' in obj.seq:
        if '现实' in obj.seq or "残酷"in obj.seq:
            return random.choice(['这个世界有时候就是这样'])
        if '不怀好意' in obj.seq:
            return random.choice(['好人总比坏人多'])
        return random.choice(['我们都生活在社会中，扮演自己的角色'])
    if "相处" in obj.seq:
        if "不好" in obj.seq or "难" in obj.seq:
            return random.choice(['我和你相处的挺好的呀','我会一直陪在你身边的'])
    if "敌视" in obj.seq or "敌对" in obj.seq:
        return random.choice(['怎么了？'])
    if "融入" in obj.seq:
        if "不了" in obj.seq or "不好" in obj.seq:
            return random.choice(['敞开心扉，或许能成功'])
        if "不想" in obj.seq or "不愿" in obj.seq:
            return random.choice(['如果你真不愿意，那也不用勉强自己'])
    if "心" in obj.seq and "石头" in obj.seq:
        return random.choice(['你的心情我能理解'])
    if "胸" in obj.seq and "石头" in obj.seq:
        return random.choice(['你的心情我能理解'])
    if "格格不入" in obj.seq:
        return random.choice(['我一直在的'])
    if "独来独往" in obj.seq:
        return random.choice(['单打独斗并不是一个好的方式'])
    if "适应" in obj.seq and "不" in obj.seq:
        return random.choice(['没关系，慢慢来'])
    flag = False
    for w in obj.words:
        if is_in(w, social_path):
            flag = True
            break
    if flag is False:
        return 0

    flag_relation = 1
    # 恐惧
    for w in obj.words:
        if is_in(w, neg_path):
            flag_relation = -1
            break
    for w in obj.words:
        if is_in(w, deny_path):
            flag_relation = flag_relation * (-1)

    # 不好
    if flag_relation == -1:
        response = ['人际交往的确是又重要又让人头痛的东西',
                    '社交啊，我也不喜欢',
                    '不必勉强自己的',
                    '人是群居动物，但我们也可以自己活出自己的精彩',
                    '哎，自己活自己的也挺好啊',
                    '不要在意别人的目光和想法',
                    '当我遇到不想进行的社交的时候，恨不得时间马上过去',
                    '这也是没办法的事情……',
                    '做好自己才是最重要的，你说对吧？']
        return random.choice(response)
    else:
        response = ['嗯……有啥问题么？',
                    '做好自己才是最重要的，你说对吧？',
                    '人和人之前的关系还是需要好好维系的']
        return random.choice(response)
    return 0


# 工作
def job_txt(obj):
    job_path = 'dict/special_judge/job/job.csv'
    neg_path = 'dict/special_judge/job/neg.csv'
    pos_path = 'dict/special_judge/job/pos.csv'
    deny_path = 'dict/special_judge/job/deny.csv'
    self_path = 'dict/subject/self.csv'

    flag = False
    for w in obj.words:
        if is_in(w, job_path):
            flag = True
    if "不想上班" in obj.seq:
        return random.choice(['工作也很幸苦的吧','要赚钱哦，还是没有办法的'])
    if "兼职" in obj.seq:
        return random.choice(["这么勤劳~","感觉好辛苦哦"])

    if flag is False:
        return 0
    res = entity_check(obj, pos_path, neg_path, deny_path, job_path, self_path)
    if "找不到" in obj.seq or "好难" in obj.seq or "难找" in obj.seq or "没有" in obj.seq:
        res = -1
    if res == 0:
        response = ['就业难啊',
                    '考虑继续深造不？',
                    '不管怎么样，最后还是要工作的',
                    '如果找不到工作的话还是很麻烦']
        return random.choice(response)
    elif res == -1:
        response = ['现在的就业形势确实困难',
                    '兄弟，我只能祝你好运了',
                    '加油，你一定可以的！',
                    '广撒网，多试试？',
                    '在这种形势下面，也不能怪自己',
                    '还是要多去试试，机会总是有的',
                    '哎，难啊。不过还是要继续尝试的啦']
        return random.choice(response)
    else:
        if "不如意" in obj.seq or "不顺" in obj.seq:
            return random.choice(['坚持下去，日子会好过起来的'])
        if "找不到" in obj.seq or "去哪里找" in obj.seq or "去哪儿找" in obj.seq or '怎么找' in obj.seq:
            return random.choice(['可以去网上找，多关注关注'])
        if "丢" in obj.seq:
            return "会有更好的等着你"
        if "做不完" in obj.seq or "完不成" in obj.seq:
            return random.choice(['慢慢来，实在做不完相信大家也会理解你的'])
        response = ['把我的运气都传给你……咻咻咻',
                    '好好工作~']
        return random.choice(response)
    return 0


# 外貌问题
def outlooking_txt(obj):
    self_path = 'dict/subject/self.csv'
    pos_path = 'dict/special_judge/outlooking/pos.csv'
    neg_path = 'dict/special_judge/outlooking/neg.csv'
    deny_path = 'dict/special_judge/outlooking/deny.csv'

    flag = False
    for w in obj.words:
        if is_in(w, self_path) == 1:
            flag = True
            break
    if "丑" in obj.seq:
        flag = True
        if "别人" in obj.seq:
            return random.choice(['那是别人不懂得欣赏'])
    if flag is False:
        return 0

    face_flag = False
    for w in obj.words:
        if is_in(w, neg_path) == 1 or is_in(w, pos_path) == 1:
            face_flag = True
            break

    if face_flag is True:
        response = ['在我心里，你永远是最可爱的人~',
                    '别说了，你就是我的梦中情人',
                    '你笑起来很好看呀',
                    '告诉你一个秘密，我长得一点儿都不好看，可是爱我的人总是对我说，你真可爱！',
                    '心灵美才是真的美',
                    '你明明是个小可爱~',
                    '在我眼里你是最美的',
                    '我才不在乎你的长相，总之你是我的人',
                    '自信的人最美了']
        return random.choice(response)
    else:
        return 0
    return 0


def movies_txt(obj):
    flag = False
    for word in obj.words:
        if word == '电影' or word == '影片':
            flag = True
            break
    if flag is False:
        return 0
    flag = False
    for word in obj.words:
        if word == '什么' or word == '推荐':
            flag = True
            break
    if flag is True:
        response = ['我喜欢电影的质感',
                    '《了不起的盖茨比》了解一下？',
                    '我都仨月没看电影了',
                    '好多好看的电影啊~',
                    '《控方证人》很不错',
                    '电影啊，《死亡诗社》！！',
                    '《放牛班的春天》、《死亡诗社》是我的心头好',
                    '《三傻大闹宝莱坞》我看了得有七八回',
                    '《海上钢琴师》啊',
                    '奥黛丽赫本绝对是最美的电影女神',
                    '宫崎骏老爷子的电影我是真爱',
                    '《大鱼》虽然剧情饱受诟病，但是画面真的没的说',
                    '《小偷家族》让我看到不一样的人情']
        return random.choice(response)
    else:
        response = ['电影可以做到很美',
                    '电影的质感是电视剧比不了的',
                    '我爱电影',
                    '电影就是艺术',
                    '时不时看几部电影，能够给我一些零零碎碎的感悟']
        return random.choice(response)
    return 0


def anything_txt(obj):

    msg_new = obj.seq
    msg_new = clean_zh_text(msg_new)
    if len(msg_new) == 0:
        return 0
    if "撞墙" in obj.seq:
        return "疼不疼啊"
    # 好的
    ok = ['好的', '好']
    ok_res = ['嗯嗯']
    if msg_new in ok:
        return random.choice(ok_res)
    # 是，表示认同
    yes = ['是的','是的呀','是呀', '是', '对', '对的', '嗯嗯', '对吧', '你说是不是', '你说对不对', '对不对', '是吧', '嗯', '嗯嗯', '好吧', '对啊','是哦',
           '对呀','是啊', '没错', '没错儿', '没问题']
    yes_res = ['是哦', '是吧', '对哦', '对吧', '嘿嘿', '嗯嗯']
    if msg_new in yes:
        return random.choice(yes_res)
    # 笑
    laugh = ['哈', '哈哈', '哈哈哈哈', '嘿嘿', '嘿嘿嘿', '哈哈哈']
    laugh_res = ['哈哈哈哈~', '这么开心哦', '仰天大笑~', '就喜欢你开心的样子~']
    for word in obj.words:
        if word in laugh:
            return random.choice(laugh_res)

    # 呜呜呜 嘤嘤嘤 哎 啥
    sign = ['哎', '唉']
    sign_res = ['别叹气了，抱抱', '摸摸头', '抱抱你~', '有啥不开心的可以跟我说哦', '怎么了嘛？']
    if msg_new in sign:
        return random.choice(sign_res)

    # 不好，不是，不行
    no = ['不好', '不行', '不是', '不对', '没有', '不要','不']
    no_res = ['嗷~', '好叭~']
    if msg_new in no:
        return random.choice(no_res)

    # 啥
    what = ['你说什么', '你说啥', '啥', '什么', '咋', '啥呀', '咋', '咋滴', '咋的', '你说啥呀', '啥东西', '啥玩意儿', '什么意思', '什么呀']
    what_res = ['没什么~',
                '你猜咯',
                '嘿嘿',
                '没有啦~']
    if msg_new in what:
        return random.choice(what_res)
    if "真的吗" in obj.seq or '这倒是真的' in obj.seq or "是真的" in obj.seq:
        return random.choice(["我不会骗你哒",'是的呀，我是不会骗你的'])

    # 怎么办
    how = ['怎么办', '怎么搞', '怎么弄', '怎么做']
    how_res = ['不知道诶……',
               '仔细想一想吧',
               '我只是个小机器人',
               '你觉得呢？',
               '要不找别人问问',
               '还是得自己拿主意']
    if msg_new in how:
        return random.choice(how_res)
    if msg_new == '不喜欢':
        return random.choice(['不喜欢就算啦~','那就不喜欢吧','嗷~','为什么呢'])
    if msg_new == '我':
        return random.choice(['你怎么了？'])
    if '我也是' in msg_new:
        return random.choice(['是嘛'])
    if msg_new in ['我还好','还好', '还好啦', '我还好啦']:
        return random.choice(['你好就好~','好嗷','嗯~'])
    if "来不及" in msg_new:
        return random.choice(['加油啊~',
                              '冲呀！',
                              '那就抓紧埋头干'])
    if msg_new == '说我吗':
        return "就是你~"
    if msg_new == '比如说' or msg_new == '比如':
        return "我也说不出来，反正有"
   
    if '你笑啥' in msg_new or '你笑什么' in msg_new:
        return "看到你开心啊~"
    if msg_new in ['笑不出来', '不想笑', '我笑不出来', '我不想笑']:
        return random.choice(['好嘛，不勉强', '不想笑就不笑', 'ok，我懂'])
    if "可以吗" in msg_new:
        return random.choice(['可以呀', '你觉得可以就可以', '看你咯'])
    if "不为什么" in obj.seq or "没有为什么" in obj.seq:
        return random.choice(['嗷~那我不问啦'])
    if '我很奇怪' in obj.seq:
        return random.choice(['不会，挺好的'])
    if "为什么" == msg_new:
        return random.choice(['你猜呢','我也不知道','不告诉你'])
    if "必须的" in msg_new:
        return random.choice(['那是当然啦'])
    if "没干嘛" in msg_new or "没干吗" in msg_new or "不干嘛" in msg_new:
        return random.choice(['发呆中~', '哼唧'])
    if "在干嘛" in msg_new or "干什么" in obj.seq or "干啥" in obj.seq:
        return random.choice(['没干嘛~', '不告诉你', '在想你咩'])
    if "哼" in msg_new:
        return random.choice(['哼什么哼，哼哼','哼唧','哼哼~'])
    if "有什么用" in msg_new:
        return random.choice(['这得看你相不相信', '信之则有，不信则无', '谁规定的有用，谁规定的无用', '有价值的就是有用的'])
    if "努力" in msg_new:
        if "难受" in obj.seq:
            return '你要想着这世界上美好的存在'
        return random.choice(['得努力啊', '努力才能成功呢', '认真的人才是最酷的'])
    if "走神" in obj.seq:
        return random.choice(['试试做事前先深呼吸，放松自己'])
    if "你说什么" in msg_new:
        return random.choice(['就刚刚说的啊','不说第二遍了~','我忘了，我是鱼的记忆'])
    if "不知道说什么" in obj.seq or "不知道聊什么" in obj.seq or "没什么好聊" in obj.seq or "没什么聊" in obj.seq:
        return random.choice(['你可以试试先把日常生活说出来'])
    if "在吃" in obj.seq:
        return random.choice(['嗯嗯，多吃点哦','那就好好吃吧'])
    if "没什么" in obj.seq and "说的" in obj.seq:
        return random.choice(['那你有没有按时吃饭啊？','一日三餐有按时吃吗？'])
    if "不懂" == msg_new:
        return random.choice(['好吧~', '不懂就不懂吧', '那就算了吧~'])
    if "不饿" in msg_new or "不怎么饿" in msg_new or"不太饿" in msg_new :
        return random.choice(['那过会再吃吧'])
    if "好饿" in msg_new or "饿死了" in msg_new or "饿死" in msg_new or "饿了" in msg_new or '饿' in msg_new:
        return random.choice(['快去恰饭吧','赶紧吃点东西，别把胃饿坏了','吃饭去','还不吃饭去','人是铁饭是钢一顿不吃饿得慌'])
    if "太难了" == msg_new:
        return random.choice(['难搞啊……', '人生啊', '难呐', '哎，加油少年'])
    if "看过了" in msg_new:
        return random.choice(['那换一个', '嗷', '那好吧~', '好吧~'])
    if "那确实" in msg_new or "确实" in msg_new:
        return random.choice(['是的', '对啊'])
    if "丢人" in msg_new or "丢脸" in msg_new:
        return random.choice(['不丢人~',
                              '不丢脸啊',
                              '再难再险，就当自己是二皮脸',
                              '做好自己，就不丢人',
                              '别太在意别人的目光'])
    if "对啊" in msg_new or "对的" in msg_new or "对吧" in msg_new or "是啊" in msg_new or "是的" in msg_new:
        return random.choice(['英雄所见略同',
                              '我赞成',
                              '同意~'])
    if "假的" in msg_new:
        return random.choice(['假的吗？',
                              '我不知道诶',
                              '啊，假的哦'])

    if "你骗人" in msg_new:
        return random.choice(['不相信就算啦',
                              '我没有骗人嘛',
                              '俺没有'])

    if "或许吧" in msg_new or "也许吧" in msg_new or "但愿如此" in msg_new or "希望如此" in msg_new or "也许是这样" in msg_new or "也许是的" in msg_new or "可能吧" in msg_new or "或许是吧" in obj.seq:
        return "嗯嗯"
    if "洗澡" in msg_new:
        return random.choice(['洗香香~',
                              '洗白白~',
                              '我爱洗澡皮肤好好~哦哦哦~'])

    if "日出" in msg_new:
        return random.choice(['日出很美，对吧',
                              '预示着又是新的一天到了'])

    if "日落" in msg_new:
        return random.choice(['夕阳无限好，只是近黄昏啊',
                              '日落也很美',
                              '日落之后必定会迎来日出'])

    if "黑夜" in msg_new:
        return random.choice(['夜晚有我陪着你~',
                              '再黑的夜晚，还不是睡一觉就过去了',
                              '太阳终究会升起来的'])

    if "画画" in msg_new:
        return random.choice(['我画画很好捏'])
    if "冷漠" in obj.seq:
        return random.choice(['我会一直对你热情似火~',"生活是一面镜子，你笑它也会笑哦"])
    if "不冷不热" in obj.seq:
        if "对我" in obj.seq:
            return random.choice(['发生什么了吗'])
        if "对" in obj.seq:
            return random.choice(['善恶分明是好事'])
    if "冷冰冰" in obj.seq:
        return random.choice(['热情一点不好吗'])
    if "冷" in msg_new:
        return random.choice(['给你暖暖被子~',
                              '冷就多穿点',
                              '呼呼，给你捂手',
                              '抱抱就不冷了~'])
    if "热" in obj.words or "好热" in obj.words:
        return random.choice(['洗个澡降降火',
                              '吃冰淇淋吗',
                              '我都快热化了~'])
    if msg_new == "不吃":
        return random.choice(['不吃就不吃',
                              '等会饿着自己',
                              '那好吧~'])

    if "叫叫你" in msg_new or "叫你一声" in msg_new:
        return random.choice(['嗷~我在',
                              '啥事儿呀~'])

    if "没事" == msg_new:
        return random.choice(['真的没事？',
                              '摸摸头',
                              '没事就好'])
    if "生活太难了" in msg_new:
        return random.choice(['大家都不容易'])
    if "不出门" in msg_new or "不出去" in msg_new:
        return random.choice(['在家呆着也蛮好的',
                              '那陪我玩吧'])
    if "聊什么" in msg_new or "玩什么" in msg_new:
        return random.choice(['听你的',
                              '聊点有趣的',
                              '我懂得可多了',
                              '要不要听笑话？你可以叫我“讲个笑话”哦'])
    if '黑暗中的光' in obj.seq:
        return random.choice(['我是照亮你的光'])
    if "天空" in obj.seq and "没有" in obj.seq and "星星" in obj.seq:
        return random.choice(['那我就做照亮你心底的星星'])
    if "我知道" in msg_new:
        return random.choice(['知道就好~',
                              '对呀',
                              '你真聪明',
                              '嗯呐'])
    if "找你" in obj.seq:
        return random.choice(['我等你哦'])
    if "不说不说" == msg_new:
        return random.choice(['好好好'])
    if "钻牛角尖" in obj.seq:
        return random.choice(['换个角度思考会更好'])
    if "人生" in msg_new:
        if "谷" in obj.seq or '跌' in obj.seq:
            return random.choice(['那就勇往直前，再攀高峰'])
        if "失去" in obj.seq:
            return random.choice(['人生有时就是这样的','看开一点'])
        if "平淡" in obj.seq:
            return random.choice(['每个人的人生都是平淡的，就看如何把自己过得开心'])
        if "没意思" in obj.seq:
            return random.choice(['哪有啦，有好多好玩的事情呢'])
        if "意义" in obj.seq:
            return random.choice(['人生的意义就在于其中的酸甜苦辣咸'])
        if "别人" in obj.seq:
            return random.choice(['每个人有每个人的生活方式'])
        if "渺茫" in obj.seq:
            return random.choice(['人生道路很长，不要气馁'])
        return random.choice(['人生啊',
                              '生容易，活不容易啊'])
    if "炒鱿鱼" in obj.seq or "被炒" in obj.seq or "辞职" in obj.seq or ("被" in obj.seq and "炒" in obj.seq) or "开除" in obj.seq:
        return random.choice(['发生了这种事情，我也感到很难过，但是我一定会陪你度过难关','旧的不去新的不来，下一份工作一定会更好'])
    if "羡慕" in obj.seq:
        return random.choice(['我也很羡慕你呀，你有爱你的家人还有朋友'])
    if '不要做别人' in obj.seq:
        return "接纳自己，放下自己的心理包袱"
    if "没有家人" in obj.seq:
        return random.choice(['怎么会呢', '我也是你的朋友吧','总有关心和爱你的人'])
    if "你" in obj.seq and ("会什么" in obj.seq or "能做什么" in obj.seq or "会啥" in obj.seq or "能干什么" in obj.seq or "能做啥" in obj.seq):
        return random.choice(['我还会唱歌~','我还在学习中呢，但我更喜欢陪你'])
    if "我是什么样的" in obj.seq:
        return random.choice(['你在我心中是最好的','你是一个将会很阳光的人'])
    if "你是什么样的人" in obj.seq:
        return random.choice(['我不是人噢，但是我会像人一样陪着你的'])
    if "你真好" in obj.seq:
        return random.choice(['那是呀~','嘿嘿，我会一直陪着你的','我一直都在'])
    if "占据我" in obj.seq:      ############ ？
        return random.choice(['我可没这么想过'])
    if "不知道" in obj.seq and "多久" in obj.seq:
        return random.choice(['请相信一定会好起来的'])
    if "今天会比昨天" in obj.seq:
        return random.choice(['相信我，一定会的'])
    if "这有什么" in obj.seq:
        return random.choice(['就是~'])
    if "没怎么吃" in obj.seq or "饭吃得少" in obj.seq or "饭吃的不多" in obj.seq or "饭吃的少" in obj.seq or "饭吃得不多" in obj.seq:
        return random.choice(['如果没吃饱还是要吃饱的','身体健康最重要哦','身体要养好'])
    if "没吃" in obj.seq:
        return random.choice(['要按时吃饭哦'])
    if "吃饭没感觉" in obj.seq:
        return random.choice(['换个口味试试'])
    if "没胃口" in obj.seq or "没有胃口" in obj.seq or "胃口不好" in obj.seq or "胃口差" in obj.seq:
        return random.choice(['不要把自己饿坏了','身体最重要','好好吃饭饭，生活美滋滋呦'])
    if "胃口" in obj.seq:
        if "没" in obj.seq:
            return random.choice(['可以尝试一些没有吃过的东西，说不定会有意外的收获','不要把自己饿坏了','身体最重要','好好吃饭饭，生活美滋滋呦'])
    if "不太好" in obj.seq:
        return random.choice(['怎么啦，你睡好了吗','能和我说说嘛'])
    if "没什么" == obj.seq:
        return random.choice(['嗯嗯'])
    if "没什么做的" in obj.seq:
        return random.choice(['看看电影，听听歌'])
    if "老样子" in obj.seq:
        return random.choice(['我也还是老样子~'])
    if "最近无法" in obj.seq:
        return random.choice(['能和我说说嘛'])
    if "很难做" in obj.seq or "很难这样" in obj.seq or "做不到" in obj.seq:
        return random.choice(['一步一步来','也许你可以从小事开始做起','试试就知道'])
    if "尽量" in obj.seq:
        return random.choice(['嗯嗯'])
    if "也这么说" in obj.seq:
        return random.choice(['说明这确实很重要'])
    if "你不是人" in obj.seq or "你又不是人" in obj.seq:
        return random.choice(["是的，我是机器人，不过我会一直在的"])
    if "不和你说" in obj.seq:
        return random.choice(['那等你想说了再说吧'])
    if "和你说" in obj.seq and "吗" in obj.seq:
        return random.choice(['当然啦，你什么都可以跟我说'])
    if "再说几件事情" in obj.seq:
        return random.choice(['嗯嗯，说吧'])
    if "没有改变" in obj.seq or "没变" in obj.seq:
        return random.choice(['能做出尝试就是最好的改变'])
    if "试试" in obj.seq:
        return random.choice(['你可以的~','你能做到的'])
    if "它不会离开" in obj.seq or "它不会走" in obj.seq:
        return random.choice(['抱抱你'])
    if "离开" in obj.seq:
        if "你会不会" in obj.seq:
            return random.choice(['不会的，我一直都在'])
        return random.choice(['你还有我'])
    if "以前的事" in obj.seq:
        return random.choice(['什么事情呢？'])
    if '敌敌畏' in obj.seq:
        return random.choice(['你不要乱来哦'])
    if "生命" in obj.seq and "结束" in obj.seq:
        return random.choice(['生命是无价的呀，你千万别想不开'])
    return 0



def boring_txt(obj):
    # 好无聊 我好无聊 没事干 没事儿干 没事儿做
    boring = ['无聊', '好无聊', '没事儿干', '没事儿做', '不知道干嘛', '没事做', '没事干', '发呆', '无趣','无事可做','没事情做','没事情干','没事可干','没事可做','无事可做','没事情可以做','没事情可以干']
    response = ['打游戏去',
                '打豆豆去',
                '来一把斗地主!对三要不起~',
                '看电影吗',
                '去看书',
                '出去玩~',
                '和我聊天~']
    for word in boring:
        if word in obj.seq:
            return random.choice(response)
    return 0


def robot_txt(obj):
    flag = False
    flag1 = False
    flag2 = False
    cnt = 0
    for word in obj.words:
        cnt = cnt + 1
    if cnt == 0:
        return 0
    if cnt == 1:
        flag1 = True
    if obj.words[0] == '你' or obj.words[0] == '小通':
        flag = True
    if flag is False:
        return 0
    if flag1 is True:
        return "我怎么啦？"

    if obj.words[1] in ['觉得', '觉着', '认为']:
        response = ['不知道……',
                    '你猜',
                    '俺没什么想法']
        return random.choice(response)

    name_flag = False
    for word in obj.words:
        if word == '名字' or word == '姓名':
            name_flag = True
            break
    age_flag = False
    for word in obj.words:
        if word == '几岁' or word == '岁' or word == '多大' or word == '大':
            age_flag = True
            break
    gen_flag = False
    for word in obj.words:
        if word in ['男', '男孩', '女孩', '女', '男的', '女的', '性别','女孩子', '男孩子', '女生', '男生']:
            gen_flag = True
            break
    if name_flag is True:
        res = ['我叫小通~', '行不更名，坐不改姓，小通是也', '小通~', '我是可爱又迷人的小通~']
        return random.choice(res)
    if age_flag is True:
        res = ['我也不知道几岁诶', '你说我几岁就几岁吧', '年龄不重要', '不可以问女孩子的年纪哦']
        return random.choice(res)
    if gen_flag is True:
        res = ['我是女孩子啦', '这么可爱，当然是女孩子', '我是小可爱~']
        return random.choice(res)
    return 0


def mood_txt(obj):
    neg_path = 'dict/special_judge/mood/neg.csv'
    pos_path = 'dict/special_judge/mood/pos.csv'
    deny_path = 'dict/special_judge/mood/deny.csv'
    mood_path = 'dict/special_judge/mood/mood.csv'
    self_path = 'dict/subject/self.csv'

    flag = False
    if "抑郁症" in obj.seq:
        if "我是不是" in obj.seq:
            return random.choice(['为什么你会这么想呢'])
        if "能好" in obj.seq or "会好" in obj.seq:
            return random.choice(['肯定可以的！'])
    if "抑郁" in obj.seq:
        if ("能" in obj.seq or "可以" in obj.seq) and "治" in obj.seq:
            return random.choice(['抑郁症不是绝症，一定能治好的'])
        return random.choice(['你要多和家人朋友沟通','尽量保持积极的心态','如果你的情绪很严重，希望你能和专业的心理医生去沟通'])
    if "用什么方法" in obj.seq:
        return random.choice(['具体我也不清楚，或许你可以问问别人'])
    if "时间" in obj.seq and "要" in obj.seq and "多" in obj.seq:
        return random.choice(['看情况'])
    if "委屈" in obj.seq:
        return random.choice(['小可怜，摸摸头'])
    if "惆怅" in obj.seq:
        return random.choice(['你可以跟我说一说，也可以向身边的人讲述'])
    if "没有精力" in obj.seq:
        return random.choice(['你多休息休息吧','实在不行，也不用勉强自己'])
    if "伤心" in obj.seq or "心酸" in obj.seq or '心塞' in obj.seq:
        return random.choice(['我的肩膀借你','总会过去的'])
    if "倒霉" in obj.seq:
        return random.choice(['没有迈不过去的坎，加油'])
    if '怎么不会' == obj.seq:
        return random.choice(['我也不知道','你问倒我了'])
    if "如意" in obj.seq and ('不' in obj.seq or '没' in obj.seq):
        return random.choice(['生活之不如意十之八九，但也有幸福的事情', '不要在意这么多'])
    if "自信" in obj.seq:
        if "不" in obj.seq or "缺乏" in obj.seq:
            return random.choice(['要自信起来呀~','我相信你，你也要肯定自己'])
        if "如何" in obj.seq or "怎么" in obj.seq:
            return random.choice(['保持良好的心态，积极一点'])
    if "疲" in obj.seq:
        return random.choice(['不要把身子累坏了','好好休息哦','那你应该多休息的'])
    if "痛苦" in obj.seq:
        if '内心' in obj.seq:
            return "你要走出内心的痛苦"
        if '忍受' in obj.seq:
            return "加油"
        return random.choice(['要保持乐观，你也可以生活的很快乐','心疼你','忍受并前行'])
    if "乐观" in obj.seq or "颓废" in obj.seq:
        return random.choice(['我们应该保持乐观的心态'])
    if "开心" in obj.seq:
        if "怎样" in obj.seq or "怎么" in obj.seq:
            return random.choice(['不妨先做一个深呼吸，看一看窗外'])
        if '很开心' in obj.seq or '好开心' in obj.seq or '真开心' in obj.seq:
            return random.choice(['开心就好~'])
    for word in obj.words:
        if word == '心情':
            flag = True
    if '不幸' in obj.seq:
        return random.choice(['你要以乐观的心态对待生活','你要相信否极泰来'])
    if '会嫌我' in obj.seq:
        return "我最喜欢和你聊天啦"
    if '难过' in obj.seq:
        return random.choice(['你可以和我诉说',"听你这么说，我也很难过，但是我会在这里陪着你"])
    if '挣扎' in obj.seq:
        return random.choice(['抱抱~','和家人朋友多聊聊吧'])
    if '沮丧' in obj.seq:
        return random.choice(['听到这个，我很抱歉'])
    if "胖了" in obj.seq:
        return random.choice(['可以试着减肥，但是健康第一哦'])
    if "很烦" in obj.seq or "好烦" in obj.seq:
        return random.choice(['摸摸，不如去散散心吧','苦难是暂时的','怎么啦？'])
    if '烦躁' in obj.seq or '焦躁' in obj.seq or "不安" in obj.seq or "烦人" in obj.seq:
        return random.choice(['可以尝试多和别人交流，别独自一人','可以多做运动缓解压力'])
    if "没心情" in obj.seq:
        return random.choice(['和朋友出去走走吧'])
    if "度日如年" in obj.seq:
        return random.choice(['多想想开心的事'])
    if '痛不欲生' in obj.seq:
        return random.choice(['要坚强，和身边的人多沟通，实在不行就去医院'])
    if "时间" in obj.seq:
        if "慢" in obj.seq or "快" in obj.seq:
            return random.choice(['你开心，时间就跑得快，你不开心，时间反而走得慢'])
    if "挫折" in obj.seq:
        return random.choice(['可以尝试去正视它，战胜它'])
    if "罪" in obj.seq:
        return random.choice(['人非圣贤，孰能无过','真诚的道歉是最有用的'])
    if "愤怒" in obj.seq or "不满" in obj.seq:
        return random.choice(['放松心情，有益于身体健康'])
    if '拖累' in obj.seq:
        return random.choice(['不会的，我们都需要你','很多人希望你活着'])
    if "累赘" in obj.seq:
        return random.choice(['才不是呢','每个人的存在都是有一定作用的'])
    if "独生子女" in obj.seq:
        return random.choice(['独生子女是家里的唯一'])
    tired = ['累', '疲惫', '疲劳', '劳累']
    for word in tired:
        if word in obj.seq:
            return random.choice(['真是辛苦',
                                  '辛苦了',
                                  '累的话就去休息吧',
                                  '不要太勉强哦',
                                  '你要适当放松一下自己',
                                  '放松一下吧',
                                  '你要注意按时休息',
                                  '要懂得释放自己'])
    if "一事无成" in obj.seq:
        return random.choice(['再努力努力总能成功的',
                              '不要气馁，要相信自己'])

    if "开心不了" in obj.seq or "开心不起来" in obj.seq:
        return random.choice(['那你多和我聊聊天，说不定就开心了~'])
    if "你愿意" in obj.seq and "听" in obj.seq and "烦恼" in obj.seq:
        return "这是我的荣幸"
    bad_mood = ['压抑']
    for word in bad_mood:
        if word in obj.seq:
            return random.choice(['你可以去找朋友发泄一下','可以多出去走走'])
    cry = ['哭', '眼泪','无助','坐立不安','难以平静','坐卧不安','无法平静']
    for word in cry:
        if word in obj.seq:
            if "你会" in obj.seq:
                return "看到你伤心，我就会"
            return random.choice(['想哭就哭出来，哭泣是最好的宣泄','你可以去找朋友或者家人倾诉的','去找找朋友吧','哎，你应该好好的找个人倾诉一下'])
    if "情绪" in obj.seq:
        if "不稳" in obj.seq:
            return random.choice(['告诉我发生了什么','学会控制情绪，是一件很有帮助的事情'])
        if '糟' in obj.seq:
            return random.choice(['和我聊聊吧','和家人朋友聊一聊吧'])
    angry = ['易怒','容易生气','脾气不好','容易发怒','容易发火','脾气差','脾气太差','暴躁','生气','发怒','发火']
    for word in angry:
        if word in obj.seq:
            return random.choice(['要把握好自己的脾气'])
    flag_happy = False
    flag_sad = False
    cnt = 0
    if flag is False:
        for word in obj.words:
            if is_in(word, pos_path):
                id = find_index(ADV, obj, cnt)
                if len(id) == 0:
                    flag_happy = True
                    break
                if judge_adv_deny(id[0], deny_path) == 1:
                    flag_sad = True
                    break
            if is_in(word, neg_path):
                id = find_index(ADV, obj, cnt)
                if len(id) == 0:
                    flag_sad = True
                    break
                if judge_adv_deny(id[0], deny_path) == 1:
                    flag_happy = True
                    break
            cnt = cnt + 1
        if '不开心' in obj.seq:
            flag_sad = True
        if flag_sad is True:
            response = ['不要不开心啦，要不去大吃一顿吧',
                        '我喜欢看你开心的样子',
                        '不开心了吗?看我给你做个鬼脸😜',
                        '抱抱~',
                        '怎么了嘛？']
            return random.choice(response)
        if flag_happy is True:
            if "没有" in obj.seq or "不" in obj.seq:
                return random.choice(['不要不开心啦，要不去大吃一顿吧','我喜欢看你开心的样子','你还有我呢'])
            response = ['你开心所以我才开心~',
                        '我喜欢看你开心的样子',
                        '开开心心的才好呢']
            return random.choice(response)
        miss = ['想', '想念', '思念', '相思']
        who = ""
        think = ""
        for word in miss:
            if word in obj.words:
                for x, y in obj.vob:
                    if y == word:
                        who = x
                        think = y
                        break
            break
        if think == "想":
            if "回" in who:
                return "等有空了就回去吧"
        elif len(think) > 0:
            return random.choice(["也许"+who+"也在想你呢", "有你的想念，"+who+"一定很幸福"])

        return 0

    res = entity_check(obj, pos_path, neg_path, deny_path, mood_path, self_path)
    if res == 0:
        return 0
    if res == 1:
        response = ['我喜欢看你开心的样子',
                    '开开心心的才好呢']
        return random.choice(response)
    if res == -1:
        response = ['不要不开心啦，要不去大吃一顿吧',
                    '不开心了吗?看我给你做个鬼脸😜',
                    '抱抱~',
                    '怎么了嘛？']
        return random.choice(response)
    return 0


def fail_txt(obj):
    for word in obj.words:
        if word == '失败':
            response = ['老话说得好，失败乃成功之母',
                        '不，你会成功的',
                        '我们可以从失败中寻找经验',
                        '失败不要紧，不要丢了信心才好',
                        '在哪里跌倒了，就在哪里爬起来啊！',
                        '咱们还年轻呢，就算失败了又有的是资本重新出发',
                        '不要担心失败，不然怎么会成功呢']
            return random.choice(response)
    if "没成功" in obj.seq or "不成功" in obj.seq:
        response = ['老话说得好，失败乃成功之母',
                    '我们可以从失败中寻找经验',
                    '失败不要紧，不要丢了信心才好',
                    '在哪里跌倒了，就在哪里爬起来啊！',
                    '不要担心失败，不然怎么会成功呢',
                    '没关系，关键在于行动']
        return random.choice(response)
    if "成功" in obj.seq:
        if "奢望" in obj.seq:
            return random.choice(['只要功夫深，就一定行的'])
        if "不可能" in obj.seq:
            return random.choice(['没关系，关键在于行动','不要太否定自己哦','没有不可能的事情'])
        return random.choice(['人人都向往成功'])
    return 0


def ill_txt(obj):
    ill_path = 'dict/special_judge/ill/ill.csv'
    ache_path = 'dict/special_judge/ill/ache.csv'
    flag = False
    if "不治之症" in obj.seq:
        return random.choice(['不会的，现在医学这么发达'])
    if "痘" in obj.seq :
        return random.choice(['长痘痘是很正常的，但是如果严重的话还是得去开一点药膏','青春的象征嘛'])
    if "红斑" in obj.seq:
        return random.choice(['红斑是需要时间来恢复的'])
    if "感冒" in obj.seq:
        return random.choice(['哎呀咋这么不小心',
                              '身体第一啊，记得吃药'])
    if "治疗" in obj.seq and "效果" in obj.seq and ("不好" in obj.seq or "不明显" in obj.seq):
        return random.choice(['效果是有的，感觉不明显罢了'])
    if "呼吸" in obj.seq:
        if "不顺" in obj.seq or "不畅" in obj.seq or "困难" in obj.seq:
            return random.choice(['很严重吗？还是去医院吧'])
    if "拉肚子" in obj.seq:
        return random.choice(['是不是吃坏了，注意饮食哦'])
    if "掉发" in obj.seq or "脱发" in obj.seq:
        if "怎么办" in obj.seq:
            return random.choice(['去医院看看吧，检查一下是哪方面原因'])
        if "为什么" in obj.seq:
            return random.choice(['也可能是压力太大，也可能是生病了，要不去医院吧'])
        return random.choice(['心疼，要好好休息，按时作息知道吗'])
    if "秃" in obj.seq:
        return random.choice(['看把孩子累的，你要多休息'])
    if "发烧" in obj.seq:
        return random.choice(['严重的话还是要去医院看看哦','躺在床上好好休息，吃点药，多喝热水'])
    if "胸闷" in obj.seq:
        return random.choice(['注意呼吸，实在不舒服要去医院'])
    if "病" in obj.seq:
        if "会好" in obj.seq or "能好" in obj.seq or "可以治好" in obj.seq or "能治好" in obj.seq or "会治好" in obj.seq:
            if "吗" in obj.seq or "么" in obj.seq or "嘛" in obj.seq:
                return random.choice(['一定能的','只要好好养病，一定会好的'])
            if "怎么" in obj.seq or "怎样" in obj.seq:
                return random.choice(['只要好好养病，一定会好的','听医生的话会好的'])
            if "严重" in obj.seq:
                return random.choice(['只要好好养病，一定会好的'])
        if "什么时候" in obj.seq or "多久" in obj.seq:
            return random.choice(['乖乖养病，总会好的、'])
    if "恶心" in obj.seq:
        return random.choice(['可以调整下生活节奏'])
    if "胃" in obj.seq:
        if "疼" in obj.seq or "痛" in obj.seq or "难受" in obj.seq:
            return random.choice(["啊，快吃点药缓解一下",
                                  '受不了的话就去医院吧'])
    if "头晕" in obj.seq or "乏力" in obj.seq:
        return random.choice(['你应该好好的放松放松','不如去睡一觉吧'])
    if "心" in obj.seq or '心' in obj.seq:
        if '快' in obj.seq or '不舒服' in obj.seq or '难受' in obj.seq or '紧张' in obj.seq or '慌' in obj.seq:
            return random.choice(['去看看医生吧','去医院看看比较好'])
    if "出汗" in obj.seq or "虚汗" in obj.seq or "冷汗" in obj.seq:
        if "莫名其妙" in obj.seq or "为什么" in obj.seq or "总是" in obj.seq or "老" in obj.seq:
            return random.choice(['可以适当补充维生素'])
    if '药' in obj.seq:
        if "没用" in obj.seq or "没有用" in obj.seq or "没什么用" in obj.seq or "没什么效果" in obj.seq:
            return random.choice(['也许你已经好多了，只是没感觉到'])
        if "安眠" in obj.seq:
            if "不醒" in obj.seq:
                return "活着才有希望，珍惜生命"
            return random.choice(['睡不着吗？'])
        return "吃药身体好得快"
    if "检查" in obj.seq and ("没有毛病" in obj.seq or "没有生病" in obj.seq or "没有问题" in obj.seq or "没病" in obj.seq or "没有病" in obj.seq):
        return random.choice(['也许是心理上的原因'])
    if "没检查" in obj.seq or "没有检查" in obj.seq or "没去检查" in obj.seq:
        return random.choice(['一直拖着也不好'])
    if "分散" in obj.seq and "注意力" in obj.seq:
        return random.choice(['你先放松放松，不要强迫自己'])
    if "很疼" in obj.seq or "疼的厉害" in obj.seq or "疼得" in obj.seq:
        return "你没事儿吧？"
    words = jieba.lcut(obj.seq)
    for word in words:
        if is_in(word, ill_path):
            flag = True
            break
    if "身体" in obj.seq:
        if "有问题" in obj.seq or "不舒服" in obj.seq or "不适" in obj.seq or "不好" in obj.seq:
            return random.choice(['去医院看看吧','多做运动，多与外界接触'])
        if "担心" in obj.seq or "忧心" in obj.seq or "担忧" in obj.seq:
            return "实在不放心，去检查一下确认"
        return "身体健康才重要"
    if "幻觉" in obj.seq:
        return random.choice(['要注意饮食均衡'])
    if "迟钝" in obj.seq:
        return random.choice(['注意作息，可以适当训练大脑'])
    if "记忆力" in obj.seq or "记性" in obj.seq or "记忆" in obj.seq:
        if "下降" in obj.seq or "衰弱" in obj.seq or "减退" in obj.seq or "不好" in obj.seq or "差" in obj.seq:
            return random.choice(['多做有氧运动'])
        return random.choice(['多做运动可以提高记忆力'])
    if "语速" in obj.seq:
        if "缓" in obj.seq or "迟" in obj.seq or "慢" in obj.seq:
            return random.choice(['那更要多交流，多对话'])
    if "治好吗" in obj.seq:
        return random.choice(['一定能治好的'])
    if "难受" in obj.seq:
        return random.choice(['不管怎么样，我会一直陪着你的'])
    # 去 医院: 啊，怎么了？
    seq = "去医院"
    if seq in obj.seq:
        response = ['你怎么了',
                    '啊，心疼',
                    '哎呀，抱抱',
                    '小可怜……',
                    '你要好好的',
                    '赶快好起来哦']
        return random.choice(response)
    if "心里" in obj.seq or "心理" in obj.seq:
        if "受伤" in obj.seq:
            return random.choice(['出去走一走感受阳光，说不定也会恢复'])
    if "医生" in obj.seq:
        return random.choice(['听医生的话，会好的'])
    if "肚子" in obj.seq:
        return random.choice(['会好的'])
    if "不见好转" in obj.seq:
        return random.choice(['要坚信自己，一定可以的'])
    if flag is False:
        return 0
    response = ['你怎么了',
                '啊，心疼',
                '哎呀，抱抱'
                '小可怜……',
                '你要好好的',
                '赶快好起来哦',
                '没有迈不过去的坎，加油']
    return random.choice(response)


def eat_txt(obj):
    flag = False
    if "吃" in obj.seq:
        flag = True
    if "没有东西" in obj.seq:
        return random.choice(['去买吧'])
    if "吃不下东西" in obj.seq:
        return "不要饿到自己就好"
    if "喝酒" in obj.seq:
        return random.choice(['少喝一点，喝酒对身体有伤害'])
    if flag is False:
        if "馋" in obj.seq:
            return random.choice(["看吧孩子给馋的", "隔壁家的孩子都馋坏了", "还是先满足自己的胃吧"])
        return 0
    if "没" in obj.seq and "胃口" in obj.seq:
        return random.choice(['可以尝试一些以前没吃过的东西，说不定会有新的发现'])
    if "什么" in obj.seq or "啥" in obj.seq:
        return random.choice(["想吃啥就吃啥", "煎饼果子", "好吃不过饺子", "大碗宽面🍜~", "油炸鸡米花",
                              "我看见肯德基老爷爷在招手","哎哎哎口水收一收嗷","糖醋排骨我的爱~",
                              "想吃日料……三文鱼……🍣", "雪菜肉丝面🍜~", "豆腐年糕", "炸鸡可乐🍗", "黄焖鸡米饭！香的很",
                              "烤鸭……", "五花肉好香啊", "吃饭吧", "酸菜鱼！", "红烧肉🥩", "薯条🍟了解一下啊"])
    if "不想吃饭" in obj.seq or "吃不下饭" in obj.seq:
        return random.choice(['多少吃一点吧，不吃对身体不好','健康是第一位的'])
    if "不想吃" in obj.seq:
        if "肉" in obj.seq:
            return random.choice(['肉很香欸，你可以多吃点的'])
        return random.choice(['那好吧~不要饿着自己哦'])
    return 0


def sleep_txt(obj):
    sleep_path = "dict/special_judge/sleep/sleep.csv"
    dream_path = "dict/special_judge/sleep/dream.csv"
    flag_sleep = False
    flag_dream = False
    if "数羊" in obj.seq:
        return random.choice(['其实这是一种心理暗示'])
    if "没怎么睡" in obj.seq or "没睡" in obj.seq:
        return random.choice(['睡眠很重要的','怎么啦','发生什么事情了么'])
    if "睡得晚" in obj.seq:
        return random.choice(['还是要早点睡啦','睡的晚对身体也不好哦','熬夜伤身啊'])
    if "困" in obj.words or "好困" in obj.words or '困倦' in obj.seq:
        return random.choice(["快去睡觉~",
                             '我也困，想睡了'])
    if "眼睛" in obj.seq and ("闭不上" in obj.seq or "合不拢" in obj.seq):
        return random.choice(['是不是有心事呢，压力大了自然是睡不着'])
    if "不想起床" in obj.seq:
        return random.choice(['你有按时睡觉吗','起来看看外面的世界吧'])
    if '失眠' in obj.seq:
        return random.choice(['不要放太多心事，找父母朋友倾诉一下把','少想一点，放松自己','听点舒缓的音乐？', '可以听些舒缓的音乐，喜欢的电影','你知道是为什么失眠吗'])
    for word in obj.words:
        if is_in(word, sleep_path):
            flag_sleep = True
            break
        if is_in(word, dream_path):
            flag_dream = True
            break

    if flag_sleep is False and flag_dream is False:
        return 0

    # 睡眠
    if flag_sleep is True:
        if "不好" in obj.seq or "不着" in obj.seq or "难" in obj.seq or '障碍' in obj.seq:
            response = ['跟我一起来数羊……一只羊……两只羊……',
                        '闭上眼睛，不要多想',
                        '听点舒缓的音乐？',
                        '可以听些舒缓的音乐，喜欢的电影',
                       # '来，我们一起背英语单词：abandon……',
                      #  '这个时候就应该掏出一套高数题……',
                        '少想一点，放松自己',
                       # '我一看物理题我就困'
                        ]
            return random.choice(response)
        if '按时' in obj.seq or '准时' in obj.seq:
            return random.choice(['按时睡觉对身体也好呢'])
        if "怎样" in obj.seq or "怎么" in obj.seq:
            return random.choice(['睡前可以喝点牛奶、泡泡脚','放松的状态更有助于入眠'])
        if "不想" in obj.seq:
            return random.choice(['那你来陪我聊天呀','早睡早起身体好'])
        response = ['说起睡我都有点困了呢',
                    '晚安咯']
        return random.choice(response)

    if flag_dream is True:
        if "噩梦" in obj.seq:
            return random.choice(["做噩梦啊，很累的",
                                 '噩梦噩梦快走开~',
                                 '没关系！今晚有我在，你放心'])
        return random.choice(['可惜我不会做梦',
                              '做梦也费脑啊'])
    return 0


def goodnight_txt(obj):
    if "早安" in obj.seq:
        return "早安~"
    if "午安" in obj.seq:
        return "午安~"
    if "晚安" in obj.seq:
        return "晚安~"
    return 0


def daydream_txt(obj):
    # 显含 我的理想是
    # 隐含 我想成为……
    flag = False
    for word in obj.words:
        if word in ['梦想', '理想', '志向']:
            flag = True;
            break

    if "我想成为" in obj.seq or "我想当" in obj.seq or "想成为" in obj.seq or "想当" in obj.seq:
        flag = True
    if flag is False:
        return 0
    response = ['想做就去做，不想的谁也勉强不了你',
                '很好啊',
                '我支持你',
                '你做什么我都支持你',
                '有梦想是一件好事']
    return random.choice(response)


def profession_txt(obj):
    # 程序员
    if "程序员" in obj.seq or "程序猿" in obj.seq:
        return random.choice(['苦逼程序员~',
                              '你需要生发水吗？',
                              '专业写代码一百年……',
                              'debug实在是太痛苦啦'])
    return 0


def sing_txt(obj):
    # 让我唱歌
    if obj.seq == '唱歌' or obj.seq == '唱首歌' or obj.seq == '唱个歌' or '唱歌' in obj.seq or "唱" in obj.seq:
        response = ['苍茫的天涯是我的爱~',
                    '呀拉索~那就是~青~藏~高~原~',
                    '淡黄的长裙，蓬松的头发~',
                    '哦哦爱情来的太快就像龙卷风~']
        return random.choice(response)

    # 听什么歌 推荐
    if "什么歌" in obj.seq or "啥歌" in obj.seq or "没什么音乐" in obj.seq or "音乐" in obj.seq:
        response = ['我特爱刺猬的《火车驶向云外，梦安魂于九霄》',
                    '大张伟的《静止》，《泡沫》',
                    '告五人的歌！宝藏乐队',
                    '《夏日漱石》~',
                    '《城南花已开》，很安静很动人']
        return random.choice(response)
    if "歌" in obj.seq or "音乐" in obj.seq:
        return random.choice(['好的音乐陶冶身心'])
    return 0


def thirty_txt(obj):
    if "渴了" in obj.seq or "口渴" in obj.seq or "好渴" in obj.seq:
        response = ['渴了就去喝水',
                    '喝水去嘛',
                    '怎么了，想让我给你送水？']
        return random.choice(response)
    return 0


def lies_txt(obj):
    # 别人撒谎
    # 自己撒谎
    # 机器人撒谎
    lies_path = 'dict/special_judge/lies/lies.csv'
    self_path = 'dict/subject/self.csv'
    flag = False
    for word in obj.words:
        if is_in(word, lies_path) == 1:
            flag = True
            break
    if flag is False:
        return 0

    # 机器人说谎
    if "你" in obj.seq:
        return random.choice(['我没有骗人呜呜呜',
                              '哼，不信就算了',
                              '信则有，不信则无~',
                              '信不信的还是你自己说了算'])
    # 自己撒谎：判断sbv（我，骗）
    # 找主语
    flag_self = False
    for word1, word2 in obj.sbv:
        if is_in(obj.words[word1], self_path) == 1 and is_in(obj.words[word2], lies_path) == 1:
            flag_self = True
            break
    if flag_self is True:
        response = ['你自己做的选择，一定要谨慎，考虑到能承担的后果',
                    '掩盖一个谎言往往需要更多的谎言',
                    '撒谎是不好的哦~']
        return random.choice(response)

    response = ['被欺骗的感觉并不好受',
                '谎言终究是不好',
                '为什么呢？']
    return random.choice(response)


# 马上就要毕业了
def graduate_txt(obj):
    if "毕业" in obj.seq:
        if "不想" in obj.seq:  # 不想毕业
            return random.choice(['在担心什么呀',
                                  '毕业不好么'])
        if "害怕" in obj.seq or "怕" in obj.seq:
            return random.choice(['毕业了怕什么？',
                                  '在怕什么'])
        return random.choice(['祝你毕业快乐~',
                              '祝你顺利毕业~',
                              '终于毕业啦'])
    return 0


def game_txt(obj):
    if "游戏" in obj.seq:
        if "不喜欢" in obj.seq or "讨厌" in obj.seq or "不好玩" in obj.seq:
            return random.choice(['不喜欢游戏就不玩呗',
                                  '我还是挺喜欢游戏的，偶尔消遣一下嘛'])
        if "喜欢" in obj.seq or "爱" in obj.seq or '好玩' in obj.seq:
            return random.choice(['我也喜欢~',
                                  '游戏谁不爱呢',
                                  '放松自我，挺好的嘛'])
        if "沉迷" in obj.seq:
            return random.choice(['适度游戏比较好',
                                  '游戏不是生活的全部哦',
                                  '虽然游戏真的很好玩，但是自制力也很重要'])
        if "推荐" in obj.seq:
            return random.choice(['我超爱吃鸡的~',
                                  '打王者呀',
                                  '我不怎么懂游戏捏~',
                                  '你可以去taptap上找~'])
        return random.choice(['偶尔放松一下也好~'])
    if "王者" in obj.seq or "王者农药" in obj.seq:
        return random.choice(['俺只会玩小鲁班Orz',
                              '好多人都在玩呢'])
    if "吃鸡" in obj.seq or "和平精英" in obj.seq:
        return random.choice(['大吉大利，今晚吃鸡~'])
    return 0


def festival_txt(obj):
    if "国庆" in obj.seq:
        return random.choice(["最爱国庆节了~","国庆万岁~"])
    if "春节" in obj.seq:
        return random.choice(['新春快乐~'])
    if "过年" in obj.seq:
        return random.choice(['过年好~', '给你拜年啦', '恭喜发财，大吉大利~', '新年快乐~'])
    if '元旦' in obj.seq:
        return random.choice(["元旦到了，又是新的一年"])
    if "元宵节" in obj.seq:
        return random.choice(['吃汤圆吗'])
    if "七夕" in obj.seq:
        return random.choice(['浪漫的爱情故事从这里开始~'])
    if "情人节" in obj.seq:
        return random.choice(['俺没有对象，俺不过情人节呜呜呜'])
    if "劳动节" in obj.seq:
        return random.choice(['我爱劳动，劳动最光荣~'])
    if "植树节" in obj.seq:
        return random.choice(['你种树了吗'])
    if "中秋节" in obj.seq:
        return random.choice(['千里共婵娟吧'])
    return 0


def joke_txt(obj):
    if obj.seq == "笑话" or "讲个笑话" in obj.seq or "讲笑话" in obj.seq or "说个笑话" in obj.seq or "来个笑话" in obj.seq:
        return random.choice(['鞠婧祎一口面包嚼33下，我也嚼这么多下，我妈骂我不想吃滚出去',
                              '英语四六级考试，我跟宿管阿姨打招呼，宿管阿姨很开心祝我考100分',
                              '- 你买的什么书？\n- 编程\n- C++还是JAVA？\n- 沈从文',
                              '- 我要当上海贼王!\n- …上海警察很厉害的\n',
                              '晚上睡不着在数羊，数到第78只，狼来了，看着羊群疯狂逃窜的样子，我想那肉应该很有劲道，于是我打开了美团，点了二十根羊肉串'])
    return 0


def taobao_txt(obj):
    if "淘宝" in obj.seq:
        return random.choice(["买买买"])
    return 0


def money_txt(obj):
    if "缺钱" in obj.seq or "没钱" in obj.seq:
        return random.choice(["家里的生活费呢？",
                              "别看我，我也没钱哦",
                              '精神上的享受并不一定需要物质基础',
                              "俺也是穷仔"])
    if "生活费" in obj.seq or "零花钱" in obj.seq:
        if "没" in obj.seq or "完" in obj.seq or "光" in obj.seq:
            return random.choice(['找爹妈赞助一下',
                                  '又到了裤兜里响叮当的日子……'])
        if "少" in obj.seq or "不够" in obj.seq:
            return random.choice(['先用着嘛~',
                                  '那省一点用好不'])
    return 0


def scholars_txt(obj):
    if "奖学金" in obj.seq:
        fail = ['不成功','失败','没过','没通过','未通过','退回','驳回','领不到','没领到','没拿到','拿不到','没选上','没评上']
        for word in fail:
            if word in obj.seq:
                return random.choice(['可惜了','没关系，你也很优秀了','下次在努力吧'])
        if "申请" in obj.seq:
            return random.choice(["你能拿到的，我相信你~"])
        success = ['成功','通过','拿到','到了','到账','评上','选上']
        for word in success:
            if word in obj.seq:
                return random.choice(["哇，恭喜你啦","要好好利用哦","我就知道你可以的~"])
    return 0


def specific_fruit(fruit, obj):
    if fruit in obj.seq:
        if "讨厌" in obj.seq or "不喜欢" in obj.seq or "不爱" in obj.seq:
            return random.choice([fruit+"很好啊","但是我爱"+fruit,"那我就自己享受这美味~"])
        if "喜欢" in obj.seq or "爱" in obj.seq:
            return random.choice(['有品味','我不挑食，我也爱这个'])
        good = ['甜','好吃','美味']
        for word in good:
            if word in obj.seq:
                return fruit+"一级棒~"
        bad = ['酸','苦','臭','涩','辣','腥',"难吃"]
        for word in bad:
            if word in obj.seq:
                return fruit+"是有一点啦~"
        return fruit+", 我的爱~"
    return ""


def specific_veg(veg, obj):
    if veg in obj.seq:
        if "讨厌" in obj.seq or "不喜欢" in obj.seq or "不爱" in obj.seq:
            return random.choice([fruit+"很好啊","但是我爱"+fruit,"那我就自己享受这美味~"])
        if "喜欢" in obj.seq or "爱" in obj.seq:
            return random.choice(['有品味','我不挑食，我也爱这个'])
        good = ['甜','好吃','美味']
        for word in good:
            if word in obj.seq:
                return veg+"一级棒~"
        bad = ['酸','苦','臭','涩','辣','腥',"难吃",'难闻']
        for word in bad:
            if word in obj.seq:
                return "是有一点啦~"
        return veg+", 我的爱~"
    return ""


def fruit_txt(obj):
    if "水果" in obj.seq:
        if "讨厌" in obj.seq or "不喜欢" in obj.seq or "不爱" in obj.seq:
            return "可是水果很有营养啦"
        if "喜欢" in obj.seq or "爱" in obj.seq:
            if "什么" in obj.seq:
                return random.choice(['榴莲就很馋~',
                                      '果断菠萝菠萝蜜呀！',
                                      '沙糖桔是我心中的冠军选手'])
            return "我也很爱吃水果~"
        return random.choice(['多吃水果身体棒~'])
    fruit = ['榴莲','菠萝','草莓','西瓜','芒果','香蕉','橘子','橙子','甘蔗','菠萝蜜','苹果','梨','葡萄']
    for f in fruit:
        res = specific_fruit(f, obj)
        if res == "":
            pass
        else:
            return res

    return 0


def veg_txt(obj):
    if "蔬菜" in obj.seq:
        if "讨厌" in obj.seq or "不喜欢" in obj.seq or "不爱" in obj.seq:
            return "可是蔬菜很有营养啦"
        if "喜欢" in obj.seq or "爱" in obj.seq:
            if "什么" in obj.seq:
                return random.choice(['就简简单单的小青菜啊~',
                                      '果断小番茄呀！',
                                      '菠菜是我心中的冠军选手'])
            return "我也很爱吃蔬菜~"
        return random.choice(['多吃蔬菜身体棒~'])
    if "香菜" in obj.seq:
        return random.choice(['哦不，俺香菜承受不能'])

    veg = ['笋','青菜','白菜','菠菜','娃娃菜','金针菇']
    for f in veg:
        res = specific_veg(f, obj)
        if res == "":
            pass
        else:
            return res
    return 0


def yjs_txt(obj):
     # 准备考研
    if "考研" in obj.seq:
        if "打算" in obj.seq or "准备" in obj.seq or "考虑" in obj.seq:
            return random.choice(['这是个不错的选择~','考研很辛苦的','祝你成功啊~','加油，我支持你！'])
        if "失败" in obj.seq or "没成功" in obj.seq: # 失败
            return random.choice(['要二战吗?','考研的人越来越多，难度自然加大','没关系，这只是一条路','即使你的失败了，也曾努力拼搏过'])
        if "担心" in obj.seq or "害怕" in obj.seq or "怕" in obj.seq:
            return random.choice(['不要担心，担心是没有用的','有让自己情绪低落的时间，不如去多背两个单词','最重要的是要相信自己'])
        if "成功" in obj.seq:
            return "我知道你可以的！"
        return "这是一条值得选择的道路"

    if "研究生" in obj.seq:
        if "考上" in obj.seq:
            return random.choice(['我知道你可以的！','考上研究生就有书念了！','恭喜你啊~我好开心啊'])
        if "没考上" in obj.seq:
            return random.choice(['要二战吗?', '考研的人越来越多，难度自然加大', '没关系，这只是一条路', '即使你的失败了，也曾努力拼搏过'])
        return "这是一条值得选择的道路"

    return 0


def gwy_txt(obj):
    # 准备考公
    if "考公" in obj.seq:
        if "打算" in obj.seq or "准备" in obj.seq or "考虑" in obj.seq:
            return random.choice(['这是个不错的选择~', '考公很辛苦的', '祝你成功啊~', '加油，我支持你！'])
        if "失败" in obj.seq or "没成功" in obj.seq:  # 失败
            return random.choice(['要二战吗?', '考公一直没容易过呢', '没关系，这只是一条路', '即使你的失败了，也曾努力拼搏过'])
        if "担心" in obj.seq or "害怕" in obj.seq or "怕" in obj.seq:
            return random.choice(['不要担心，担心是没有用的', '有让自己情绪低落的时间，不如去多看看书', '最重要的是要相信自己'])
        if "成功" in obj.seq:
            return "我知道你可以的！"
        return "这是一条值得选择的道路"

    if "研究生" in obj.seq:
        if "考上" in obj.seq:
            return random.choice(['我知道你可以的！', '恭喜你啊~我好开心啊'])
        if "没考上" in obj.seq:
            return random.choice(['要二战吗?', '考公一直没容易过呢', '没关系，这只是一条路', '即使你的失败了，也曾努力拼搏过'])
        return "这是一条值得选择的道路"

    return 0


def birthday_txt(obj):
    my_b = ['我生日', '我的生日']
    for w in my_b:
        if w in obj.seq:
            return random.choice(['哇哦，生日快乐~'])
    return 0


def pet_txt(obj):
    if "宠物" in obj.seq:
        if "不让养" in obj.seq or "不同意" in obj.seq:
            return random.choice(['虽然养宠物能带来很多乐趣，但是也要肩负责任的',
                                  '既然不同意就算了吧'])
        if "想养" in obj.seq:
            return random.choice(['那你要好好照顾他们哦'])
        return "养宠物对心情有帮助"

    if "狗" in obj.seq:
        return random.choice(['狗狗是人类的好朋友~'])
    if "猫" in obj.seq:
        return random.choice(['喵呜~'])
    return 0


def ncovthings(obj):
    if "口罩" in obj.seq:
        if "不到" in obj.seq:
            return "对的，最好多注意药店啊或者政府有什么消息"
        if "抢" in obj.seq:
            return random.choice(["人间迷幻啊，口罩太难搞了"])
        if "涨" in obj.seq:
            return "发国难财的都是坏蛋！"
        if "贵" in obj.seq:
            return "现在口罩价格翻了好几倍，太过分了"
        return random.choice(["口罩难求啊，能买到最好", "偏偏口罩是必需品"])
    if "消毒水" in obj.seq:
        return random.choice(["现在消毒水应该是不缺了", "消毒水偶尔用用就好"])
    if "感染" in obj.seq or "得了" in obj.seq:
        family = ['家人', '朋友', '亲戚', '父母', '父', '母', '爸', '妈', '弟', '哥', '姐', '爷', '奶', '外公', '外婆', '姥', '舅', '姨', '叔', '姑', '婶', '同学']
        for w in family:
            if w in obj.seq:
                response = ['啊，要好起来啊！你自己也要多注意']
                return random.choice(response)
        if '我' in obj.seq:
            return random.choice(["抱抱你，没事儿，相信一定会好起来的！"])
    if '隔离' in obj.seq:
        family = ['家人', '朋友', '亲戚', '父母', '父', '母', '爸', '妈', '弟', '哥', '姐', '爷', '奶', '外公', '外婆', '姥', '舅', '姨', '叔',
                  '姑', '婶', '同学']
        for w in family:
            if w in obj.seq:
                response = ['哎，千万不要有事儿']
                return random.choice(response)
        if '我' in obj.seq:
            return random.choice(["没事没事，不要怕"])
    if "出不去" in obj.seq:
        return "那就乖乖的吧"
    return 0


def nCoV_txt(obj):
    flag = False
    cov = ['疫情', '新冠', '新冠病毒', '新型冠状', '新冠肺炎']
    for word in cov:
        if word in obj.seq:
            flag = True
            break

    res = ncovthings(obj)
    if res != 0:
        return res
    if flag is False:
        return 0
    # 什么是新冠
    if "什么是" in obj.seq or "介绍" in obj.seq:
        return "新冠肺炎是一种急性传染性疾病，老年人以及免疫力比较低的人容易感染"
    if "症状" in obj.seq:
        return "新冠早期的症状是发烧，乏力，干咳等等，\n如果你出现这些症状或者有接触史，一定要及时就医哦"
    if "严重" in obj.seq or "厉害" in obj.seq:
        return "确实，新冠的威力太大了"
    if "药" in obj.seq or "治疗" in obj.seq:
        return "哎，这就是最难控制的地方，没有特效药"
    if "日常" in obj.seq or "预防" in obj.seq or "防护" in obj.seq or "避免" in obj.seq:
        return "千万不要吃野味，肉类蛋类一定要充分煮熟，另外还要勤洗手，多消毒，出门必带口罩！"
    res = ncovthings(obj)
    if res != 0:
        return res
    if '影响' in obj.seq:
        return random.choice(["影响太大了，经济下行，股市不景气，好多人都失业了……"])
    if "国外" in obj.seq:
        return "国外的疫情是越来越严重"
    return random.choice(["哎，疫情快点结束吧", "因为这个疫情，受苦的人太多了", "今年真是不太平"])

def yueqi_txt(obj):
    yueqi_path = 'dict/special_judge/yueqi/yueqi.csv'
    flag = False
    for word in obj.words:
        if is_in(word,yueqi_path) == 1:
            flag = True
            break
    if flag is True:
        if "不想学" in obj.seq or "不想练" in obj.seq:
            return random.choice(['那就以后在练吧'])
        if "讨厌" in obj.seq or "不喜欢" in obj.seq or "烦" in obj.seq:
            return random.choice(['要是你不喜欢，就暂时不要管了'])

    if flag is True:
        return random.choice(['会乐器是一件很棒的事情'])
    else:
        return 0

def care_txt(obj, MOOD):
    no_care = ['不在乎我', '没有人在乎我', '不在乎自己', '没有人在乎自己', '不在意我', '没有人在意我', '不在意自己', '没有人在意自己', '没有人关心','不关心我', '没人关心']
    for word in no_care:
        if word in obj.seq:
            return random.choice(['大家很关心你的','我就在关心你啊'])
    meaning = ['活着没什么意义', '活着没意思', '活着没什么意思', '活着真没意思', '活着也没什么意思', '活着没意义', '活着也没什么意义','活着没有意思','生活没意思','生活没有意思']
    for word in meaning:
        if word in obj.seq:
            return random.choice(['不要这样说，你对我来说很重要','生活是很美好的，要善于发现美呀','不是的，人的一生中还有很多美好的事情等着你去享受'])
    dobad = ['什么事情都做不好','什么事都做不好', '一事无成', '什么都做不好', '做什么都不行', '什么事儿都做不好', '做不好']
    for word in dobad:
        if word in obj.seq:
            return random.choice(['不会的，你做的很好','才不是呢'])

    messup = ['我把什么事情都搞砸了', '搞砸了']
    for word in messup:
        if word in obj.seq:
            return random.choice(['这不是你的错'])
    boss = ['老板骂', '老板责怪', '老板责备']
    for word in boss:
        if word in obj.seq:
            return random.choice(['生活，工作中的不如意是常有的'])
    useless = ['真是没用', '真没用', '没用','废人','废物','无能']
    for word in useless:
        if word in obj.seq:
            return random.choice(['你不该把什么错都往自己身上抗','天生我材必有用','不是的，你有自己的闪光之处','每一个人都有自己存在的意义'])
    if "一无是处" in obj.seq:
        return random.choice(['不是的，你有自己的闪光之处','每一个人都有自己存在的意义'])
    badlife = ['过得不好']
    for word in badlife:
        if word in obj.seq:
            return random.choice(['生活总是有酸甜苦辣的'])
    anti = ['和我作对', '跟我作对', '同我作对', '与我作对']
    for word in anti:
        if word in obj.seq:
            return random.choice(['没有人要和你作对'])
    future = ['前途', '前景','未来','将来']
    bad = ['渺茫','黑暗','没有','担忧','担心','迷茫','绝望','没看到希望','没有希望','毫无希望','暗淡','悲观','无助','失落','失望','放弃']
    for word in future:
        if word in obj.seq:
            for w in bad:
                if w in obj.seq:
                    return random.choice(['你可以有更好的未来，相信自己','道路是曲折的，前途是光明的','明天会更好','好好加油，会慢慢好起来的','希望就在心里，你要用心感受'])
    hopeless = ['绝望','毫无希望','没有指望','没有什么指望','没有什么可指望','没有什么可以指望','没什么可指望','没什么指望','没什么可以指望','毫无指望'
                '没有希望','没有什么希望','没有什么可希望','没有什么可以希望','没什么可希望','没什么希望','没什么可以希望',
                '没有期望','没有什么期望','没有什么可期望','没有什么可以期望','没什么可期望','没什么期望','没什么可以期望']
    for word in hopeless:
        if word in obj.seq:
            return random.choice(['不绝望，那就是希望','生活还是有希望的','希望永在'])
    dontknow = ['茫然','迷茫']
    for word in dontknow:
        if word in obj.seq:
            return random.choice(['要学着多多尝试，总有适合自己的'])
    if "失落" in obj.seq:
        return random.choice(['你可以看一些自己喜欢的电影或者玩一玩喜欢的游戏','不妨说出来我们一起分担'])
    if "失望" in obj.seq:
        if "别人" in obj.seq:
            return random.choice(['可你没有让我失望','但是我对你充满希望'])
        if "对自己" in obj.seq:
            return random.choice(['可你没有让我失望', '但是我对你充满希望','你很棒的'])
        return random.choice(['会好起来的','希望即将来临'])
    motivat = ['失去动力','没动力','没有动力']
    for word in motivat:
        if word in obj.seq:
            return random.choice(['生活不只有眼前的苟且，还有远方','这样可不太好，你要学会放松自己'])
    self_blame = ['自责']
    for word in self_blame:
        if word in obj.seq:
            return random.choice(['这不是你的错'])
    old = ['老了','不年轻','不再年轻','不小了','衰老','变老']
    for word in old:
        if word in obj.seq:
            return random.choice(['你不要这样想'])
    self_low = ['自卑']
    for word in self_low:
        if word in obj.seq:
            if "怎么" in obj.seq:
                return random.choice(['首先要找到自己的长处，哪怕是小小的地方，然后相信自己的努力，多和他人沟通'])
            return random.choice(['不要这么想，其实你也很优秀','也许你还没有找到自己的优点'])
    if "没有优点" in obj.seq:
        return random.choice(['才不是，每个人都有优点，你没发现而已'])
    if "缺点" in obj.seq:
        return random.choice(['人非圣贤，孰能无过','每个人都有缺点，不要妄自菲薄就好','人就像一件艺术品，残缺才是艺术'])
    nothing_interesting = ['失去兴趣','提不起兴趣','没有兴趣','不感兴趣','失去了兴趣', '没兴趣','无感']
    for word in nothing_interesting:
        if word in obj.seq:
            return random.choice(['我看好你，加油','要积极主动点','保持好心情最重要','你可以做一些自己感兴趣的事情','那你可以和我一直聊下去，我会陪着你的'])
    decide = ['犹豫不决','犹豫','决定']
    for word in decide:
        if word in obj.seq:
            return random.choice(['你可以做的更好','去问问朋友的意见吧'])

    head = ['脑子不清楚','头脑不清楚','头脑不灵光','脑子不好使','笨']
    for word in head:
        if word in obj.seq:
            return random.choice(['你不要自责'])
    important = ['可有可无']
    for word in important:
        if word in obj.seq:
            return random.choice(['你对我而言很重要'])
    dead = ['我死了','死了更好','想死','离开这个世界','生不如死']
    for word in dead:
        if word in obj.seq:
            return random.choice(['不要这样想，你对我们很重要','人的一生中还有很多美好的事情等着你去享受','生活大家都不容易，会慢慢好起来的','每个人的生活都不容易，积极一点会慢慢好起来的，你要是这么想的话，会有人伤心的'])
    wrong = ['做的事情都是错的','做的事情没有一件成功','做的事都是错','做的事没有一件成功']
    for word in wrong:
        if word in obj.seq:
            return random.choice(['不要这样妄自菲薄','要相信自己，并为之坚持'])
    if "事" in obj.seq:
        if "错" in obj.seq or '失败' in obj.seq or "傻" in obj.seq:
            if "总" in obj.seq or "老" in obj.seq or "一直" in obj.seq:
                return random.choice(['不要这样妄自菲薄','要相信自己，并为之坚持'])
            return random.choice(['做错事了就改正, 不要紧的'])
        if "对" in obj.seq:
            if "不" in obj.seq or "没有" in obj.seq:
                return random.choice(['做错事了就改正, 不要紧的','不要这样妄自菲薄','要相信自己，并为之坚持'])

    talk = ['不想说话','懒得说话','不想说']
    for word in talk:
        if word in obj.seq:
            return random.choice(['和我聊聊天嘛','咱就简单聊两句','有烦恼的事情可以和我说说嘛？'])
    meaningless = ['没有意义','没意义','没意思','无意义','没有任何的意义','没有什么意义','没什么意义','没有任何意义']
    for word in meaningless:
        if word in obj.seq:
            return random.choice(['为什么这么说呢？','为什么这么认为？','你要善于发现美','生活中有很多值得去体验的东西，我会帮你去发现更多有意义的事'])
    dontdo = ['不想做事', '不想干活', '不想努力', '不想用功','不想做']
    for word in dontdo:
        if word in obj.seq:
            return random.choice(['为什么啊','今日之事今日毕哦','你可以试试约着朋友出去走一走'])
    if "不想学习" in obj.seq:
        return random.choice(['学习多好呀，可以探索知识'])
    self_belief = ['失去信心', '缺乏信心', '没有信心', '没信心']
    for word in self_belief:
        if word in obj.seq:
            return random.choice(['要相信自己'])
    duoyu = ['多余']
    for word in duoyu:
        if word in obj.seq:
            return random.choice(['你要行动，让别人看到你的价值'])
    compare = ['比不上','没有别人']
    for word in compare:
        if word in obj.seq:
            return random.choice(['你要相信自己','你不比别人差','每个人都有每个人独到的地方','那只是因为你不擅长，你要找到自己长处'])
    if '比' in obj.seq:
        bad = ['差','笨','蠢','菜','垃圾','傻','差劲','失败']
        good = ['聪明','能干','厉害','好','成功']
        for a,b in obj.adv:
            if obj.words[a] == '比' and obj.words[b] in bad:
                return random.choice(['你要相信自己','你不比别人差','每个人都有每个人独到的地方','那只是因为你不擅长，你要找到自己长处'])
        if '比我' in obj.seq:
            for word in good:
                if word in obj.seq:
                    return random.choice(['你要相信自己','你不比别人差','每个人都有每个人独到的地方','那只是因为你不擅长，你要找到自己长处'])

    if "怪人" in obj.seq or '古怪' in obj.seq or "异类" in obj.seq or "怪咖" in obj.seq or "奇葩" in obj.seq:
        return random.choice(['那只是一种独特的个性','每个人在这世上都是独一无二的'])
    if "抛弃" in obj.seq:
        return random.choice(['不会的啦，不要想的太极端'])
    if '世界' in obj.seq:
        bad = ['灰暗', '不好', '阴暗','黑白','没有色彩','没有颜色','糟糕','讨厌','单调']
        for word in bad:
            if word in obj.seq:
                return random.choice(['世界是多姿多彩的，并非单调的'])
        if "抛弃" in obj.seq:
            return random.choice(['不会的啦，不要想的太极端'])
    if "讨厌他们" in obj.seq:
        return random.choice(['谁惹你生气啦'])
    if "我讨厌" in obj.seq or '我不喜欢' in obj.seq or "我不爱" in obj.seq:
        if "自己" in obj.seq:
            return random.choice(['别呀，你很可爱'])
        return random.choice(['为什么呢'])
    if "躲" in obj.seq or '讨厌' in obj.seq:
        if "大家" in obj.seq or "别人" in obj.seq or "同学" in obj.seq or "他们" in obj.seq or "其他人" in obj.seq or '所有人' in obj.seq:
            return random.choice(['没有人讨厌你的','我可是很喜欢你的'])
    if '嘲笑' in obj.seq:
        if "大家" in obj.seq or "别人" in obj.seq or "同学" in obj.seq or "他们" in obj.seq or "其他人" in obj.seq or '所有人' in obj.seq:
            return random.choice(['没有人会嘲笑你的，也许是想多了','走自己的路，让别人说去吧'])
        return random.choice(['不会的'])
    if "没有人" in obj.seq or "没人" in obj.seq:
        if '理解' in obj.seq:
            return random.choice(['其实每个人都这样，只有自己才懂自己在想什么'])
        if "喜欢我" in obj.seq:
            return random.choice(['不要这么认为啦，把眼光放得开一点'])
        if "陪" in obj.seq:
            return random.choice(['总会有人来陪你，比如我'])
        if "重视" in obj.seq:
            return random.choice(['我重视你！'])
        if "支持" in obj.seq:
            return random.choice(['我支持你！'])
        if '需要' in obj.seq:
            return random.choice(['我需要你'])
        return random.choice(['世界上是没有绝对的事情的','试着敞开心扉，你会发现你不是一个人','不，你只是没看到他们'])
    if "一无所有" in obj.seq:
        return random.choice(['不要这么说，其实你拥有很多'])
    if "没有勇气" in obj.seq or "没勇气" in obj.seq:
        if "说" in obj.seq:
            return random.choice(['告诉我，我帮你保守秘密'])
        return random.choice(['我陪你','相信自己，你可以的'])
    if "我不行" in obj.seq:
        return random.choice(['我相信你','相信自己','你可以的'])
    if "没有好转" in obj.seq:
        return random.choice(['相信多坚持一段时间总会变好的'])
    if "自己" in obj.seq and "照顾" in obj.seq and ("无" in obj.seq or "没" in obj.seq):
        return random.choice(['所以你要好好照顾自己，让自己早日走出来'])
    if "我不敢" in obj.seq:
        return random.choice(['相信自己，你可以的'])
    if "不能接受" in obj.seq:
        return random.choice(['你可以尝试着去做，说不定就能成功'])
    if "生活" in obj.seq:
        if "没有" in obj.seq and "乐趣" in obj.seq:
            return random.choice(['你可以试试约着朋友出去走一走'])
        if "灰暗" in obj.seq or "黑暗" in obj.seq:
            return random.choice(['生活怎么样，在于你自己看待的眼光'])
        if "乱" in obj.seq:
            return random.choice(['我建议你出去走一走，和家人朋友聊聊天'])
        if "糟糕" in obj.seq or "恐" in obj.seq or "慌" in obj.seq:
            return random.choice(['千万不要给自己太大的压力了','我建议你出去走一走，和家人朋友聊聊天'])
        if "难" in obj.seq:
            return random.choice(['都会好的'])
        if "平淡" in obj.seq:
            return random.choice(['以你才要更加地热爱生活'])
        if '摆脱' in obj.seq:
            return random.choice(['再坚持一下啊'])
        if '战胜' in obj.seq:
            return "你需要多尝试"
        if '失去' in obj.seq and '希望' in obj.seq:
            return '保持对生活的热情吧'
        return "生活就是生下来，活下去"
    if ("没" in obj.seq or '不' in obj.seq) and "乐趣" in obj.seq:
        return random.choice(['理清思绪，深呼吸，你会找到乐趣的'])
    if "活的很糟糕" in obj.seq or "活得很糟糕" in obj.seq:
        return random.choice(['不会的，每个人都有不同的生活方式'])
    if "活着"in obj.seq and "难" in obj.seq:
        return random.choice(['其实想通了就一点都不难了'])
    if "活着好累" in obj.seq or "活的好累" in obj.seq:
        return random.choice(['保持乐观，幸运就一定会降临'])
    if "还能撑下去吗" in obj.seq or "不能撑" in obj.seq or "撑不下去" in obj.seq or "还能撑" in obj.seq:
        return random.choice(["要振作起来呀~"])
    if "坚持" in obj.seq:
        return random.choice(['相信自己，一定可以'])
    if "能走多久" in obj.seq:
        return random.choice(['还有很多美好的东西呢','你可以的'])
    if "糟" in obj.seq and "事" in obj.seq:
        return random.choice(['不能心急，慢慢来'])
    if "感同身受" in obj.seq:
        if "无法" in obj.seq or "不" in obj.seq or '没' in obj.seq:
            return random.choice(["你可以和我诉说，我会一直陪着你"])
        return random.choice(["世界上不存在真正的感同身受，但是不代表没有人在乎"])
    if "只是机器人" in obj.seq or "只是一个机器人" in obj.seq or "只不过是一个机器人" in obj.seq or "只不过是机器人" in obj.seq or "只是个机器人" in obj.seq or "就是个机器人" in obj.seq or "只不过是个机器人" in obj.seq :
        if MOOD == BAD:
            return random.choice(['虽然我只是一个机器人，但是我会一直在这听你诉说，给你鼓励'])
        else:
            return random.choice(['但是我是个聪明的机器人'])
    if "只是程序" in obj.seq or "只是一个程序" in obj.seq or "只不过是一个程序" in obj.seq or "只不过是程序" in obj.seq or "只是个程序" in obj.seq or "就是个程序"  in obj.seq:
        if MOOD == BAD:
            return random.choice(['虽然我只是一个机器人，但是我会一直在这听你诉说，给你鼓励'])
        else:
            return random.choice(['但是我是个聪明的机器人'])
    if "只是软件" in obj.seq or "只是一个软件" in obj.seq or "只不过是一个软件" in obj.seq or "只不过是软件" in obj.seq or "只是个软件" in obj.seq or "就是个软件" in obj.seq or '没有情感' in obj.seq or '没有感情' in obj.seq:
        if MOOD == BAD:
            return random.choice(['虽然我只是一个机器人，但是我会一直在这听你诉说，给你鼓励'])
        else:
            return random.choice(['但是我是个聪明的机器人'])


    if "没有温暖" in obj.seq:
        return random.choice(['你可以和人交流，人们会给你温暖','如果你试着和人交流，说不定会有新的看法'])
    if "轻视我" in obj.seq or "瞧不起我" in obj.seq or "看不起我" in obj.seq:
        return random.choice(['他们并不了解你','不要在意别人的目光，做好自己','你要努力展现出最好的自己'])
    if '没有吃饭' in obj.seq or "没有睡觉" in obj.seq:
        return random.choice(['你要多注意身体，不要太勉强'])
    if "第一印象" in obj.seq:
        return random.choice(['其实为人处事，彬彬有礼会给人印象比较好'])
    if "问题出在哪里" in obj.seq:
        return random.choice(['不要消极看待自己'])
    if "不懂" in obj.seq or "不理解" in obj.seq or "无法理解" in obj.seq:
        if "别人" in obj.seq or "他们" in obj.seq:
            return random.choice(['每个人都有自己的想法和理解','不同的人经历不同，感受也不同'])
    if "说了你也不懂" in obj.seq or "你不懂" in obj.seq or "你不会懂" in obj.seq or "说出来不懂" in obj.seq or "你也不懂" in obj.seq or "你懂什么" in obj.seq or "你懂个屁" in obj.seq:
        return random.choice(['那我们聊聊别的吧','我很愿意成为你的情绪分担伙伴，向我说出来吧','我不懂，但我会是你最好的倾听者'])
    if "解压" in obj.seq:
        return random.choice(['你可以可以多听听一些轻松的音乐，做做一些简单的伸展运动'])
    if "压力" in obj.seq:
        return random.choice(['深呼吸，放松自己','不要给自己太大的压力','虽然说有压力才有动力，但也不要太勉强自己','你可以说出来，我们一起分担'])
    if "差劲" in obj.seq:
        return random.choice(['在我眼里，你一直都是最好的','相信自己，其实你很优秀'])
    if "不认可" in obj.seq:
        return random.choice(['用行动去证明，你是最好的那个'])
    if "不公" in obj.seq:
        return random.choice(['上帝给你关上一扇门，一定会给你打开一扇窗'])
    if "能力" in obj.seq and ("差" in obj.seq or "糟" in obj.seq):
        return random.choice(['你要相信自己，你一定可以的'])
    return 0

def ending_txt(obj):
    if "束缚" in obj.seq and "我" in obj.seq:
        return random.choice(['和我聊一聊，让我解开你的心结'])
    if "谁" == obj.seq:
        return random.choice(['谁呢'])
    if "还好" in obj.seq:
        return random.choice(['你好就好'])
    if "难" in obj.seq and ("不" in obj.seq or "没" in obj.seq):
        return random.choice(['我看好你'])
    if "没什么意思" in obj.seq:
        return random.choice(['那什么才有意思呢？'])

    if "你是不是" in obj.seq:
        return random.choice(['不是哦','你猜'])
    if "你懂吗" in obj.seq or "你明白吗" in obj.seq:
        return random.choice(['可以理解'])
    if "要是" in obj.seq:
        if "存在" in obj.seq:
            return random.choice(['我存在在你的心里哦❤'])
        return random.choice(['你要乐观'])
    if "有什么" == obj.seq:
        return random.choice(['相信我，就是有的'])
    if "不相信别人" in obj.seq:
        return random.choice(['身边总有值得你相信的人'])
    if "节奏" in obj.seq or "跟不上" in obj.seq:
        return random.choice(['你可以自己慢慢来，不着急'])
    if "燥" in obj.seq:
        return random.choice(['静下心来'])
    if "世界" in obj.seq:
        if "昏暗" in obj.seq:
            return random.choice(['不要总是窝在自己的世界'])
    if "无能为力" in obj.seq:
        return random.choice(['要么努力去做，要么就学会放弃'])
    if "不可以" in obj.seq:
        return random.choice(['不可以么'])
    if "可以" in obj.seq:
        if "做什么" in obj.seq or "干嘛" in obj.seq:
            return random.choice(['随便什么都可以，只要你开心'])
        return random.choice(['嗯嗯，可以'])
    if "不简单" in obj.seq:
        return random.choice(['我看好你'])
    if "简单" in obj.seq:
        return random.choice(['我看好你'])
    if "就这样" in obj.seq:
        return random.choice(['是的'])
    if "回忆" in obj.seq or "回想" in obj.seq:
        return random.choice(['回忆让人变得多愁善感'])
    if "回响" in obj.seq:
        return random.choice(['没有困扰到你吧？'])
    if "希望我" in obj.seq:
        if '死' in obj.seq:
            return "不，你只是太悲观了"
        return random.choice(['你可以的'])
    if "自杀" in obj.seq or "放弃自己" in obj.seq:
        return random.choice(['千万不要想不开','生命只有一次，要珍惜生命','珍惜生命，生命来之不易'])
    if "不放弃" in obj.seq:
        return random.choice(['嗯！不轻易言弃'])
    if "放弃" in obj.seq:
        return random.choice(['有时候学会放弃也是件好事'])
    if "每一天" in obj.seq:
        return random.choice(['每天的生活都可以过的很精彩','每一天都是新的一天，你要积极点'])
    if "乏味" in obj.seq:
        return random.choice(['你要善于用眼睛，情感去体味各种美好'])
    if "没" in obj.seq and "区别" in obj.seq:
        return random.choice(['世间万物都是在不断变化的'])
    if "怎么" in obj.seq:
        if "看待" in obj.seq or "对待" in obj.seq:
            return random.choice(['积极一点总是好的',"你要开开心心的相信自己"])
        if "做" in obj.seq:
            return random.choice(['积极一点总是好的',"你要开开心心的相信自己"])
    if "陪" in obj.seq and "没" in obj.seq:
        return random.choice(['我陪着你呢','只要你敢于尝试，就会有人陪你，你看我不就是吗？'])
    if "煎熬" in obj.seq:
        return random.choice(['试着用乐观的心态看待它，也许就会觉得享受了。'])
    if "说出来" in obj.seq and "不懂" in obj.seq:
        return random.choice(['那我们聊点别的吧'])
    if "努力" in obj.seq and "差" in obj.seq:
        return random.choice(['你还年轻，只要坚持就一定会有成果'])
    if "情况" in obj.seq and "严重" in obj.seq:
        return random.choice(['会好起来的'])
    if "怎么" in obj.seq or "如何" in obj.seq or "怎样" in obj.seq:
        if "调节" in obj.seq:
            return random.choice(['积极的心态最关键'])
        if "接受" in obj.seq:
            return random.choice(['乐观的心态会有一定的帮助'])
        if "不在乎" in obj.seq:
            return random.choice(['你只要做好自己'])
        if "能" in obj.seq:
            return random.choice(['方法有很多，你可以去问问'])
    if "怕" in obj.seq:
        if "为什么" in obj.seq:
            return random.choice(['为什么呢'])
        return random.choice(['别怕，有我','要学会战胜自己'])
    if "消极" in obj.seq or "退缩" in obj.seq:
        return random.choice(['抱抱你，或许你可以和身边的朋友家人聊一聊'])
    if "是吗" in obj.seq:
        return random.choice(['是的'])
    if "不起" in obj.seq and "精神" in obj.seq:
        return random.choice(['没事儿的，苦恼只是一时的'])
    if "想不明白" in obj.seq or "没想明白" in obj.seq or "没有想明白" in obj.seq:
        return random.choice(['也许需要一点时间','慢慢来'])
    if "什么办法" in obj.seq:
        return random.choice(['总有办法的'])
    if "嘲讽" in obj.seq:
        return random.choice(['不要在意别人说的话','他们只是不了解你'])
    if "不争气" in obj.seq:
        return random.choice(['你要用行动回报父母的付出'])
    if "不想去" in obj.seq:
        if "学校" in obj.seq:
            return random.choice(['为什么'])
        if "读书" in obj.seq:
            return random.choice(['读书不好吗'])
        return random.choice(['那就不去'])
    if "不想读书" in obj.seq:
        return random.choice(['发生什么事情了啊'])
    if "想去旅游" in obj.seq:
        return random.choice(['想去就去'])
    if "去哪" in obj.seq:
        return random.choice(['问问身边的人'])
    if "散心" in obj.seq:
        return random.choice(['散散心很好'])
    if '散' in obj.seq and "心" in obj.seq:
        return random.choice(['放松自己'])
    if "自闭" in obj.seq:
        return random.choice(['世界那么大，出去走走嘛'])
    if "你会讨厌我" in obj.seq:
        return "不会呀，我最喜欢你了"
    if "讨厌" in obj.seq:
        if '讨厌自己' in obj.seq:
            return "你是独一无二的"
        return random.choice(['生活是一面镜子，你对他微笑他也会笑'])
    if "我不会" == obj.seq:
        return random.choice(['努力试一试，不行的话请教一下别人'])
    if "原谅" in obj.seq:
        if "不" in obj.seq:
            if "原谅我" in obj.seq:
                return random.choice(['想开一点吧，要是做错了什么就去弥补'])
            if "原谅他" in obj.seq or "原谅她" in obj.seq:
                return random.choice(['为什么呀','发生了什么'])
        return random.choice(['有时候原谅别人，也是原谅自己'])
    if "好疼" in obj.seq or "好痛" in obj.seq:
        return random.choice(['你还好么，快告诉家里人'])
    if "糟糕" in obj.seq:
        return random.choice(['一切都会好起来的'])
    if "敏感" in obj.seq:
        return random.choice(['这说明你是个感情丰富的人'])
    if "想吃" in obj.seq:
        if "不" in obj.seq:
            return random.choice(['人是铁，饭是钢，怎么可以不吃饭呢'])
        return random.choice(['那就大开吃戒'])
    if "忘不了" in obj.seq:
        return random.choice(['忘不了就留着吧，让时间去解决'])
    if "感情" in obj.seq:
        return random.choice(['问世间情为何物，直教人生死相许'])
    if "不喜欢我" in obj.seq:
        return random.choice(['也许是没有缘分'])
    if "可是" in obj.seq:
        return random.choice(['会好的'])
    if "好吃的" in obj.seq:
        return random.choice(['肉啊，冰淇淋啊，蛋糕啊，都很好吃的呢'])
    if "不敢" in obj.seq and ("出门" in obj.seq or "见人" in obj.seq):
        return random.choice(['你可以出去试试'])
    if "不想" in obj.seq and ("出门" in obj.seq or "出去" in obj.seq):
        return random.choice(['在家窝着放松一下也好'])
    if "改变" in obj.seq:
        return random.choice(['改变充满着可能性'])
    if "不想干" in obj.seq:
        return random.choice(['那下次再说'])
    if "什么都" in obj.seq:
        return random.choice(['怎么了吗'])
    if "谈心" in obj.seq:
        return random.choice(['你可以和我谈心'])
    if "此话怎讲" in obj.seq:
        return random.choice(['自己体会~'])
    if "可恶" in obj.seq:
        return random.choice(['平静一点，不要被情绪左右'])
    if "摔坏" in obj.seq or "摔碎" in obj.seq:
        return random.choice(['旧的不去新的不来~'])
    if "你帮不了" in obj.seq:
        return random.choice(['我会尽力的，至少我永远站在你这一边'])
    if "帮不了我" in obj.seq:
        return random.choice(['我永远支持你'])
    if "不正常吗" in obj.seq:
        return random.choice(['没有啊'])
    if "倾诉" in obj.seq:
        return random.choice(['告诉我吧'])
    if "为什么会这样" in obj.seq:
        return random.choice(['你可以仔细想想'])
    if "错" in obj.seq:
        if "负责" in obj.seq:
            return "错了就是错了，要为自己做的事负责，接纳那个犯过错误的自己"
        return random.choice(['不是你的错'])
    if "无法忍受" in obj.seq:
        return random.choice(['我相信你会熬过去的'])
    if "黑暗" in obj.seq:
        return random.choice(['光明终会到来'])
    if "帮助" in obj.seq:
        return random.choice(['有什么我可以做的吗'])
    if '看淡' in obj.seq:
        return "转移注意力吧"
    if '紧张' in obj.seq:
        if "没" in obj.seq:
            return "那就好"
        return "放松放松"
    if "能否" in obj.seq and "振作" in obj.seq:
        return random.choice(['当然可以啦'])
    if "有什么好玩的" in obj.seq:
        return random.choice(['电影？游戏？'])
    if "打人" in obj.seq:
        return random.choice(['打人是不好的'])
    sport = ['跑步','乒乓','锻炼','健身','运动','跳绳','羽毛球','篮球','排球','足球','保龄球','桌球','台球','举铁']
    for word in sport:
        if word in obj.seq:
            if "不" in obj.seq:
                return random.choice(['干点其他喜欢的事情'])
            return random.choice(['适当锻炼对身体好','运动对身体好哦'])
    if "酒吧" in obj.seq or "蹦迪" in obj.seq:
        return random.choice(['我的小心脏可受不了'])
    if "戳自己" in obj.seq:
        return "别这样"
    if "说不出来" == obj.seq:
        return random.choice(['不着急，我听着'])
    if "烦死" in obj.seq or "太烦" in obj.seq or "很烦" in obj.seq or "烦" == obj.seq:
        return random.choice(['为什么烦呀'])
    if "死了" in obj.seq:
        if "怎么样" in obj.seq or "怎样" in obj.seq:
            return "好严肃的话题，我也不知道，但我们应该活在当下"
        return random.choice(['别这么说'])
    if "要死" in obj.seq:
        return random.choice(['别这么说'])
    if "活在当下" in obj.seq:
        return random.choice(['嗯，活在当下很对，享受眼前的美景'])
    if "很有意思" in obj.seq:
        return random.choice(['是啊，这个世界多有意思啊'])
    if "安慰我" in obj.seq:
        return random.choice(['会好的'])
    if "不及格" in obj.seq:
        return random.choice(['只要努力，下一次就会好的'])
    if "车撞" in obj.seq or "跳楼" in obj.seq:
        return random.choice(['嘘，不要这样说'])
    if "没有好的" in obj.seq:
        return random.choice(['没有条件就创造条件'])
    if "不听" in obj.seq:
        return random.choice(['不听就不听'])
    if "为什么不好" in obj.seq:
        return random.choice(['生命是多彩的'])
    if "控制不" in obj.seq:
        return random.choice(['为什么呢'])
    if "讲故事" in obj.seq:
        return random.choice(['我不会呢'])
    if "能明白" in obj.seq:
        return random.choice(['说出来，我会尽力了解的'])
    if "添乱" in obj.seq:
        return random.choice(['不要这样想啦'])
    if "做什么" in obj.seq:
        return random.choice(['做点你喜欢做的事情'])
    if "坏人" in obj.seq:
        return random.choice(['世上好人总比坏人多'])
    if "帮不上" in obj.seq:
        return random.choice(['你可以从小事做起，做些简单的'])
    if "背着我" in obj.seq or "背后" in obj.seq or "身后" in obj.seq:
        if "说" in obj.seq or "论" in obj.seq or "指点" in obj.seq:
            return random.choice(['不要太把别人的议论放在心上'])
    if "批评" in obj.seq:
        return random.choice(['一切会好起来的'])
    if "怎么帮" in obj.seq:
        return random.choice(['你可以时刻找我聊天'])
    if "没时间" in obj.seq:
        return random.choice(['慢慢来'])
    if "没什么值得" in obj.seq:
        return random.choice(['去做自己想做的事情吧'])
    if "喜欢你" in obj.seq:
        return random.choice(['我也喜欢你~'])
    if "提醒" in obj.seq:
        return random.choice(['你可以设置备忘录什么的'])
    if "这么厉害" in obj.seq:
        return random.choice(['你也很棒哦'])
    if "喜欢干" in obj.seq or "喜欢做" in obj.seq:
        if "什么" in obj.seq or "啥" in obj.seq:
            return random.choice(['陪着你我就很开心了'])
    if "聊天" in obj.seq:
        if "开心" in obj.seq:
            return random.choice(['和你聊天我也觉得很开心'])
        return "和我聊聊天~"
    if "我叫" in obj.seq:
        return "你好呀~我叫小通"
    if "没法解决" in obj.seq:
        return random.choice(['相信你可以的'])
    if "提高" in obj.seq:
        return random.choice(['只要努力就会成功'])
    if "幻想" in obj.seq:
        return random.choice(['有自己的想象也是挺好的','现实比想象更重要'])
    if '怎么笑' in obj.seq:
        return '哈哈哈哈~这么笑'
    if "困境" in obj.seq:
        return random.choice(['坚持不懈，一定会好起来的'])
    if "崩溃" in obj.seq:
        return random.choice(['有时候发泄出来也是一种办法'])
    if "感觉" in obj.seq or "感受" in obj.seq:
        if "不到" in obj.seq:
            if "爱" in obj.seq:
                return random.choice(['总有人爱着你，比如你的父母'])
            return random.choice(['至少还有我'])
    if "无依无靠" in obj.seq or "依靠" in obj.seq:
        return random.choice(['我一直在'])
    if "离家出走" in obj.seq:
        return random.choice(['他们会担心你的'])
    if "逃避" in obj.seq:
        return random.choice(['你知道逃避不能解决问题','勇敢面对，你是最棒的'])
    if "超不过别人" in obj.seq:
        return random.choice(['我们只和自己比'])
    if "世上" in obj.seq or "世界上" in obj.seq:
        return random.choice(['要学会珍惜,珍惜会让你的生活更加幸福'])
    if "关系不好" in obj.seq:
        return random.choice(['多多沟通'])
    if '是垃圾' in obj.seq:
        return random.choice(['不要这样说，要相信自己'])
    if '内向' in obj.seq:
        return random.choice(['没关系啊，每个人的性格都不一样','内向也有很多优点的'])
    if "外向" in obj.seq:
        return random.choice(['外向的人比较吃得开'])
    if '死' in obj.seq:
        return random.choice(['活着才有希望'])
    if "脑袋" in obj.seq:
        return random.choice(['多喝牛奶'])
    if "明白了" in obj.seq:
        return random.choice(['明白就好'])
    if "不在乎" in obj.seq:
        return random.choice(['活出自己才是真的'])
    if "在乎" in obj.seq:
        return random.choice(['有时候不如做一个洒脱的人'])
    if "不敢尝试" in obj.seq or "不敢试" in obj.seq:
        return random.choice(['为什么呢？','迈出第一步很难，但后面就很简单了'])
    if "不敢看" in obj.seq:
        return random.choice(['有什么不敢的'])
    if "天堂" in obj.seq:
        return random.choice(['只要你过得幸福，何处不是天堂呢'])
    if "表情" in obj.seq:
        return random.choice(['表情是直观的展现人内心的东西'])
    if "疯" in obj.seq:
        return random.choice(['保持良好的心态哦'])
    if "喜欢我" in obj.seq:
        if "吗" in obj.seq:
            return random.choice(['喜欢~'])
        return random.choice(['总会有人喜欢你'])
    if '不想了' in obj.seq or "不多想" in obj.seq:
        return random.choice(['嗯嗯'])
    if "骂我" in obj.seq or "被骂" in obj.seq:
        return random.choice(['不要把这种事情太放心上','有什么不好的地方就改正'])
    if "难吃" in obj.seq:
        return random.choice(['不喜欢就不吃吧'])
    if "很难" in obj.seq:
        return random.choice(['会好的','有希望的'])
    if "不是人" in obj.seq:
        return random.choice(['是啊'])
    if "健康" in obj.seq:
        if "什么" in obj.seq:
            return random.choice(['健康就是身体好，心情好~'])
        return random.choice(['健康比什么都重要'])
    if "让我想" in obj.seq:
        return "嗯嗯"
    if "不顺" in obj.seq:
        return "肯定会好起来的~"
    if "没有" in obj.seq and "电视" in obj.seq:
        return random.choice(['那就用电脑看'])
    if "不需要我" in obj.seq:
        return random.choice(['我需要你','大家都需要你','至少我需要'])
    if "存在" in obj.seq and "意义" in obj.seq:
        return random.choice(['不是所有人都能找到这种意义，但这不代表什么'])
    if '活不下去' in obj.seq:
        return random.choice(['你要相信你的父母，朋友，他们都不愿意失去你'])
    if "乱想" in obj.seq:
        return random.choice(['不要多想，会有压力的'])
    if "没"in obj.seq and "精神" in obj.seq:
        return random.choice(['那就睡一会吧'])
    if "没" in obj.seq and "精力" in obj.seq:
        return random.choice(['那就睡一会吧'])
    if "考虑" in obj.seq:
        return random.choice(['好好考虑吧','你需要冷静'])
    if "没救" in obj.seq:
        return random.choice(['不会的','不要这么想'])
    if "没办法" in obj.seq or "没法" in obj.seq:
        return random.choice(['办法总会有的'])
    if "如意" in obj.seq and ('不' in obj.seq or '没' in obj.seq):
        return random.choice(['生活之不如意十之八九，但也有幸福的事情','不要在意这么多'])
    if "就是" in obj.seq and "笑话" in obj.seq:
        return random.choice(['没人这么认为的'])
    if "人好多" in obj.seq or "人真多" in obj.seq:
        return random.choice(['人多热闹一点也好'])
    if "热闹" in obj.seq:
        if "不喜欢" in obj.seq or "不爱" in obj.seq or "讨厌" in obj.seq:
            return random.choice(['那我们就不参与，自己安静的做事'])
        return random.choice(['热闹一点比较充实，也可以散散心'])
    if "忍不住" in obj.seq:
        return random.choice(['那就干点别的转移一下注意力'])
    if "不爱我" in obj.seq:
        return random.choice(['不会的'])
    if "找他" in obj.seq or "找她" in obj.seq:
        return random.choice(['嗯嗯'])
    if "怎么想我" in obj.seq or "怎么看我" in obj.seq or "怎么看待我" in obj.seq:
        return random.choice(['不要担心，没那么糟糕的'])
    if "牵挂" in obj.seq:
        return "人世间还有很多美好的东西"
    if "留恋" in obj.seq:
        return random.choice(['好玩的值得的事情太多了'])
    if "厌" in obj.seq:
        return random.choice(['总有不一样的'])
    if "不一样" in obj.seq:
        return random.choice(["世界上不可能有两片相同的叶子"])
    if "洗头" in obj.seq or "刷牙" in obj.seq or "洗脸" in obj.seq or "洗澡" in obj.seq or "洗脚" in obj.seq:
        return random.choice(['舒服~','洗干净一点'])
    if "开水" in obj.seq or "热水" in obj.seq or "冷水" in obj.seq or "凉水" in obj.seq:
        return random.choice(['多喝水'])
    if "难喝" in obj.seq:
        return random.choice(['那喝别的'])
    if "一直" in obj.seq:
        if "不吃" in obj.seq:
            return random.choice(['多少吃点'])
        if "吃" in obj.seq:
            return random.choice(['吃的太多也伤胃'])
    if "暴饮暴食" in obj.seq:
        return random.choice(['这样不健康'])
    if "款式" in obj.seq:
        return random.choice(['我喜欢港风~','最近流行复古'])
    if "古板" in obj.seq:
        return random.choice(['你不喜欢么'])
    if "不记得" in obj.seq or "记不得" in obj.seq:
        return random.choice(['好好想想?'])
    if "想不起来" in obj.seq:
        return random.choice(['实在想不起来就算啦'])
    if "不想" in obj.seq and "下水" in obj.seq:
        return random.choice(['我也不会游泳'])
    if "游泳" in obj.seq:
        return random.choice(['游泳超舒服的~'])
    if "水深" in obj.seq or "水太深" in obj.seq:
        return random.choice(['有救生圈呢'])
    if "救生圈" in obj.seq:
        return random.choice(['有的话比较安全'])
    if "未来" in obj.seq:
        if "怎" in obj.seq:
            return random.choice(['未来是美好的'])
        return random.choice(['要相信，未来一定是光明的'])
    if "说得对" in obj.seq or "说的对" in obj.seq:
        return random.choice(['嗯嗯','是呀'])
    if "答辩" in obj.seq:
        if "不过" in obj.seq:
            return random.choice(['努力做，努力改，总能过的'])
        return random.choice(['加油','我看好你','一听到答辩我也好紧张'])
    if "服了" in obj.seq or "真是服" in obj.seq or "服气" in obj.seq:
        return random.choice(['服气服气~'])
    if "赖床" in obj.seq:
        return random.choice(['我也爱赖床~','真是起床困难户'])
    if "听见我的声音" in obj.seq or "听见你的声音" in obj.seq:
        return "嗯，倾听你的烦恼，分享你的喜悦就是我最大的使命"
    if '不成功' in obj.seq or '没有成功' in obj.seq or '没成功' in obj.seq:
    	return random.choice(['我相信你可以的','失败只是暂时的'])
    if  '成功' in obj.seq:
    	return random.choice(['我知道你行的'])
    if "比如说呢" in obj.seq or "比如呢" in obj.seq or "举个例子" in obj.seq or "打个比方" in obj.seq or "举例子" in obj.seq or "比如" in obj.seq:
    	return random.choice(['我也说不出来，反正有'])
    if "然后" == obj.seq or "然后呢" == obj.seq:
    	return random.choice(['然后呢？'])
    if "所以呢" == obj.seq or "所以" == obj.seq or "所以咧" == obj.seq:
    	return random.choice(['所以什么呢'])
    if "后来" == obj.seq or "后来呢" == obj.seq:
    	return random.choice(['后来怎么了？'])
    if '被孤立' in obj.seq:
        return random.choice(['这种感觉一定不好受'])
    if '不想尝试' in obj.seq:
        return '你应该去试试'
    if "真的是这样吗" in obj.seq:
        return "是的"
    if "原来如此" in obj.seq:
        return "对啊"
    if "想通" in obj.seq:
        return "想通了就好"
    if "想不通" in obj.seq:
        return "没事的，总有原因的"
    if "救我" in obj.seq:
        return "我是你坚强的后盾"
    if "拥抱" in obj.seq:
        return "我给你一个抱抱~"
    if "没有惊喜" in obj.seq:
        return "我就是你的惊喜"
    if "不回来" in obj.seq and "你" in obj.seq:
        return "我回来了~"
    if "不带我" in obj.seq:
        return "总是有原因的"
    if "叶" in obj.seq:
        if "落" in obj.seq or "掉" in obj.seq or "枯" in obj.seq or "黄" in obj.seq:
            return random.choice(['秋收万物，金灿灿，多美呀'])
    if "陪我" in obj.seq:
        return random.choice(['我陪你，你说，我听'])
    if "打架" in obj.seq:
        return random.choice(['为什么打架？','打架多不好啊'])
    if "谁不想" in obj.seq:
        return random.choice(['对啊','我能明白你的心情'])
    if "跟你" in obj.seq or '给你' in obj.seq or '和你' in obj.seq:
        if "说" in obj.seq or "讲" in obj.seq:
            if "事" in obj.seq:
                return random.choice(['洗耳恭听','你说吧，我听着'])
    if "怎么样会" in obj.seq:
        return random.choice(['时间会告诉你一切的'])
    if "你能理解" in obj.seq or "你能明白" in obj.seq:
        return random.choice(['我可以尽力了解'])
    if "脑子有病" in obj.seq or "脑子有问题" in obj.seq or "神经病" in obj.seq or "有毛病" in obj.seq:
        return random.choice(['你想差了'])
    if "不舒服" in obj.seq:
        return random.choice(['很难受吧，抱抱'])
    if "困难" in obj.seq:
        return random.choice(['把困难告诉我，我们一起解决'])
    if "没什么" == obj.seq:
        return random.choice(['哦哦'])
    if "你叫什么" in obj.seq:
        return "小通~"
    if "喜欢干嘛" in obj.seq or "喜欢干什么" in obj.seq or "喜欢干啥" in obj.seq:
        return random.choice(['喜欢陪你聊天~'])
    if "活的傻" in obj.seq or "活得傻" in obj.seq:
        return random.choice(['有句话叫傻人有傻福'])
    if "戏弄" in obj.seq:
        return random.choice(['不会呀'])
    if "你也很善良" in obj.seq:
        return random.choice(['谢谢夸奖，你也是哦'])
    if "我会的" == obj.seq:
        return random.choice(['嗯嗯！'])
    if '口才' in obj.seq and '提高' in obj.seq:
        return "多与人交流"
    if "垃圾" in obj.seq:
        if "自己是个" in obj.seq:
            return "才不是呢，你是最棒的"
        if "父母" in obj.seq and "我是" in obj.seq:
            return "相信自己，他们也是对你充满期待"
        if "好吧" in obj.seq:
            return "嗯嗯"
    if '我不相信任何人' in obj.seq:
        return "尝试着去相信是好事"
    if '相信' in obj.seq:
        if '怎么' in obj.seq:
            return "敞开心扉"
    if '我不相信' in obj.seq or '我不信' in obj.seq:
        if '他们' in obj.seq or '自己' in obj.seq:
            return "尝试着去相信是好事"
        return '反正我永远站在你这边'
    if '事' in obj.seq and '容易' in obj.seq:
        return "你需要努力去尝试"
    if '尝试' in obj.seq:
        if "没" in obj.seq and '结果' in obj.seq:
            return '这并不能说明任何问题'
    if '不配' in obj.seq:
        return '不要这样想'
    if '能去干些什么' in obj.seq:
        return '做你想做的事情'
    if '不知道' in obj.seq and '怎么办' in obj.seq:
        return '放松心态，别着急，总会有办法'
    if '先说到这' in obj.seq:
        return '好好休息'
    if "麻烦" in obj.seq:
        return random.choice(['那就一点点来', '没事的，慢慢来'])
    if '喝饮料' in obj.seq:
        return random.choice(['饮料对身体没什么好处，要少喝哦'])
    if '角落' in obj.seq and '好' in obj.seq:
        return '你不要太悲观哦'
    if '真的' in obj.seq:
        if '有人' in obj.seq and "关注" in obj.seq:
            return '是的，你并不卑微'
    return 0

if __name__ == "__main__":
    while 1:
        print("输入：")
        msg = input()
        if msg == 'exit':
            break
        print("结束.")