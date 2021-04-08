import pandas as pd
import random
from analyze_attr import sign_sub
from analyze_attr import sign_predicate
from analyze_attr import sign_obj_predicate
from analyze_attr import sign_adverbial
from analyze_attr import sign_ADV_Relation
from analyze_attr import get_qgxs
import re

#计算情绪积极或消极性
def neg_or_pos_cal(text):
    predict.classifier.initialize()
    x = predict(text)
    print(x)
    return x


# 主语是心情
def sub_entity1_and_predicate(attr_dict):
    a = random.random()
    positive_list_path = 'dict/emotion_dict/pos_all_dict.csv'
    negative_list_path = 'dict/emotion_dict/neg_all_dict.csv'
    adverbial_word_path = 'dict/emotion_dict/deny.csv'
    sign_sub(attr_dict["subject"])  #主语
    sign_predicate(attr_dict["predicate"], positive_list_path, negative_list_path)
    sign_adverbial(attr_dict["adverbial"], adverbial_word_path)
    tag = attr_dict["predicate"][1] * attr_dict["adverbial"][1] if attr_dict["adverbial"]!=[] else attr_dict["predicate"][1]
    #print("**********************")
    #print(attr_dict["subject"][1])
    #print(attr_dict["predicate"][1])
    if attr_dict["subject"][1] == 0 and (tag <= -1):
        if attr_dict["subject"][0] == "房间" or attr_dict["subject"][0] == "房子":
            return "你是觉得孤独了吗？那我们来聊聊天吧"
        elif a < 0.25:
            return "不妨试试把精力放在对自己而言重要的事情上"
        elif a < 0.5:
            return "为什么会有这种想法呢，你愿意和我分享下吗？"
        elif a < 0.75:
            return "你可以试着和我沟通，排解心中的苦闷"
        elif a < 1:
            return "来吧，在我这里你可以表达任何想法，我就是你的树洞，我听得见你的声音。"
    else:
        return ""


# 主语是物体2，身体
def sub_entity2_and_predicate(attr_dict):
    positive_list_path = 'dict/emotion_dict/pos_all_dict.csv'
    negative_list_path = 'dict/emotion_dict/neg_all_dict.csv'
    adverbial_word_path = 'dict/emotion_dict/deny.csv'
    sign_sub(attr_dict["subject"])
    sign_predicate(attr_dict["predicate"], positive_list_path, negative_list_path)
    sign_adverbial(attr_dict["adverbial"], adverbial_word_path)
    #print("**********************")
    #print(attr_dict["subject"][1])
    #print(attr_dict["predicate"][1])
    #print(attr_dict["adverbial"][1])
    if attr_dict["subject"][1] == 2 and (attr_dict["predicate"][1] * attr_dict["adverbial"][1] == -1):
        a = random.random()
        if a < 0.15:
            answer = "心理上的伤害可以向我诉说，但身体上的不适真的需要找专业的医生去看看哦！"
        elif a < 0.3:
            answer = "哎呀，心疼，要赶快好起来呀"
        elif a < 0.45:
            answer = "不舒服吗？真可惜我不是医生，要保护好自己啦！"
        elif a < 0.6:
            answer = "如果你生病了，我会好担心你的啊"
        elif a < 0.75:
            answer = "生病了？不舒服？哎呀，真让人心疼！你要多注意身体嘛"
        elif a < 0.9:
            answer = "真的很不舒服的话，一定要去医院哦！不然我会很担心你的，爱你的人也会很挂念你。"
        else :
            answer = "你要放松心态，要多注意饮食，多休息"
        return answer
    else:
        return ""


# 主语是自己， 宾语
def sub_entity_and_obj(attr_dict):
    pre_list_path = 'dict/sub_obj/pre.csv'
    obj_list_path = 'dict/sub_obj/obj.csv'
    sign_sub(attr_dict["subject"])
    sign_obj_predicate(attr_dict["predicate"], pre_list_path)
    if attr_dict["subject"][1] == 1 and (attr_dict["predicate"][1] == 1):
        return "继续保持积极的心态吧~"
    elif attr_dict["subject"][1] == 1 and (attr_dict["predicate"][1] == -1):
        return random.choice(['说来听听？','我明白你的意思','出啥事儿了？','怎么了'])


# 主语是物，根据时间差判断给出答复
# 时间通过ADV关系找到，并根据ADV中的relation判断程度词
def delta_time(attr_dict, info_entity):
    sign_sub(attr_dict["subject"])
    a = random.random()
    if attr_dict["subject"][1] == 0:
        if sign_ADV_Relation(info_entity) == 1:     # 前后+坏好
            if a < 0.5:
                return "嗯嗯，既然今天心情不错，要一直这样下去哦"
            elif a < 1:
                return "希望你每天都像这样开开心心哒，就像小太阳，走到哪里哪里亮~"
        elif sign_ADV_Relation(info_entity) == 2:   # 前后+好坏
            if a < 0.5:
                return "嗯，心情不好的时候就去散散步啊，听听歌啊啥的"
            elif a < 1:
                return "是有什么烦心的事情困扰着你吗？你可以和我聊聊吗"
        elif sign_ADV_Relation(info_entity) == 3:   # 后前+坏好
            if a < 0.5:
                return "心静即声淡，其间无古今。平时你可以看看美丽的风景，听听平时喜欢的音乐，慢慢调整自己的状态"
            elif a < 1:
                return "是有什么烦心的事情困扰着你吗？你可以和我聊聊吗"
        elif sign_ADV_Relation(info_entity) == 4:   # 后前+好坏
            if a < 0.5:
                return "你真棒，要继续这样保持下去，保持乐观的心态，多多调整自己"
            elif a < 1:
                return "继续保持积极的心态，积极的人像太阳，走到哪里哪里亮。相信你可以做到的"
    else:
        return ""


# 主语是自己，谓语动词是情绪
def PreEmotion__DenyAdv(attr_dict):
    a = random.random()
    positive_list_path = 'dict/emotion_dict/pos_all_dict.csv'
    negative_list_path = 'dict/emotion_dict/neg_all_dict.csv'
    adverbial_word_path = 'dict/emotion_dict/deny.csv'
    sign_sub(attr_dict["subject"])
    sign_predicate(attr_dict["predicate"], positive_list_path, negative_list_path)
    sign_adverbial(attr_dict["adverbial"], adverbial_word_path)
    #print("**********************")
    #print(attr_dict["predicate"][1])
    #print(attr_dict["adverbial"][1])
    if attr_dict["subject"][1] == 1 and attr_dict["predicate"][1] * attr_dict["adverbial"][1] == -1:
        response = ["我想看到你100%的笑容",
                    "怎么了嘛",
                    "具体和我说说？",
                    "开心一点嘛",
                    "笑一笑没什么大不了"]
        return random.choice(response)
    else:
        return ""

# 主语是自己，谓语动词是动词（无聊）
def self_boring(attr_dict):
    a = random.random()
    positive_list_path = 'dict/emotion_dict/pos_all_dict.csv'
    negative_list_path = 'dict/emotion_dict/boring.csv'
    adverbial_word_path = 'dict/emotion_dict/deny.csv'
    sign_sub(attr_dict["subject"])
    sign_predicate(attr_dict["predicate"], positive_list_path, negative_list_path)
    sign_adverbial(attr_dict["adverbial"], adverbial_word_path)
    # print("**********************")
    # print(attr_dict["predicate"][1])
    # print(attr_dict["adverbial"][1])
    if attr_dict["subject"][1] == 1 and attr_dict["predicate"][1] == -1:
        if a < 0.25:
            return "那我们来聊聊天吧，你可以和我分享下最近有什么烦恼"
        elif a < 1:
            return "要不来一局俄罗斯方块小游戏解解闷"
    else:
        return ""

# 主语是自己，谓语是动词（相信）
def sub_belief(attr_dict):
    a = random.random()
    positive_list_path = 'dict/sub_self_pre/action_pos.csv'
    negative_list_path = 'dict/sub_self_pre/belief.csv'
    adverbial_word_path = 'dict/emotion_dict/deny.csv'
    sign_sub(attr_dict["subject"])
    sign_predicate(attr_dict["predicate"], positive_list_path, negative_list_path)
    sign_adverbial(attr_dict["adverbial"], adverbial_word_path)
    # print("**********************")
    # print(attr_dict["predicate"][1])
    # print(attr_dict["adverbial"][1])
    if attr_dict["subject"][1] == 1 and attr_dict["predicate"][1] * attr_dict["adverbial"][1] == -1:
        response = ['不要这么想啦',
                    '你可以的！',
                    '我觉得学会相信也很重要',
                    '要学会冷静分析',
                    '无论如何，有我相信你',
                    '我始终站在你那一边',
                    '摸摸头',
                    '抱抱你']
        return random.choice(response)
    else:
        return 0

# 主语是自己，谓语是动词（无用）
def sub_self_and_pre(attr_dict):
    a = random.random()
    positive_list_path = 'dict/sub_self_pre/action_pos.csv'
    negative_list_path = 'dict/sub_self_pre/action_neg.csv'
    adverbial_word_path = 'dict/emotion_dict/deny.csv'
    sign_sub(attr_dict["subject"])
    sign_predicate(attr_dict["predicate"], positive_list_path, negative_list_path)
    sign_adverbial(attr_dict["adverbial"], adverbial_word_path)
    #print("**********************")
    #print(attr_dict["predicate"][1])
    #print(attr_dict["adverbial"][1])
    if attr_dict["subject"][1] == 1 and attr_dict["predicate"][1] * attr_dict["adverbial"][1] == -1:
        if a < 0.5:
            return "你要相信自己。"
        elif a < 0.75:
            return "不要怕，不要紧张"
        elif a < 1:
            return "别着急，你有什么不明白的可以和我说说，说不定我能给你一些建议呢"
    else:
        return ""


# 主语是他人(你)，谓语是动词
def sub_other1_and_pre(attr_dict):
    positive_list_path = 'dict/emotion_dict/pos_all_dict.csv'
    negative_list_path = 'dict/emotion_dict/neg_all_dict.csv'
    adverbial_word_path = 'dict/emotion_dict/deny.csv'
    sign_sub(attr_dict["subject"])
    sign_predicate(attr_dict["predicate"], positive_list_path, negative_list_path)
    sign_adverbial(attr_dict["adverbial"], adverbial_word_path)
    #print("**********************")
    #print(attr_dict["predicate"][1])
    #print(attr_dict["adverbial"][1])
    if attr_dict["subject"][1] == 3 and attr_dict["predicate"][1] * attr_dict["adverbial"][1] == -1:
        return "我们可以聊聊开心的事情"
    else:
        return ""


# 主语是他人，谓语是动词
def sub_other2_and_pre(attr_dict):
    a = random.random()
    positive_list_path = 'dict/emotion_dict/pos_all_dict.csv'
    negative_list_path = 'dict/emotion_dict/neg_all_dict.csv'
    adverbial_word_path = 'dict/emotion_dict/deny.csv'
    sign_sub(attr_dict["subject"])
    sign_predicate(attr_dict["predicate"], positive_list_path, negative_list_path)
    sign_adverbial(attr_dict["adverbial"], adverbial_word_path)
    #print("**********************")
    #print(attr_dict["predicate"][1])
    #print(attr_dict["adverbial"][1])
    if attr_dict["subject"][1] == -1 and attr_dict["predicate"][1] * attr_dict["adverbial"][1] == -1:
        if a < 0.25:
            return "别人怎么样才不管呢，做好你自己才是啊，我永远支持你啦~"
        elif a < 0.5:
            return "人和人之间的牵绊是很奇妙的东西，如果你想要维持好的关系，就需要自己也承担一些责任。"
        elif a < 0.75:
            return "相信自己，也相信别人，多沟通也是个好办法。"
        else :
            return "行为认知疗法中认为，有时候过于情绪化会影响自己对事物的判断。希望你能正确认识到这些。"
    else:
        return ""


# 直接根据情绪的极性进行问答，这里完善情感强度
def emotion_polarity(s1, input_data):
    a = random.random()
    generator = get_qgxs(s1)
    res_msg = ""
    for angry_qgxs, evil_qgxs, fear_qgxs, sad_qgxs, shocked_qgxs, not_happy_qgxs, not_good_qgxs in generator:
        if (angry_qgxs > evil_qgxs and angry_qgxs > fear_qgxs and angry_qgxs > sad_qgxs and angry_qgxs > shocked_qgxs):
            if (angry_qgxs > 0):
                qg = 'angry'
                if (a < 0.05):
                    res_msg = '让自己不生气不是忍，而是打内心明白生气的原理和危害，才能从根本上杜绝生气给身体造成的伤害。 '
                elif (a < 0.1):
                    res_msg = '别生气啦~要不我们去打一把游戏解解气？还有好多有趣的事情等着你呢。'
                elif (a < 0.15):
                    res_msg = '生气不如争气，发火不如发奋。'
                elif (a < 0.2):
                    res_msg = '不然去休息一下，先把讨人厌的事情放一放怎么样？'
                elif (a < 0.25):
                    res_msg = '对于一些让自己生气的事，当怒则怒，该忍则忍。 '
                elif (a < 0.3):
                    res_msg = '有人说“忍字心上一把刀”,可见“忍气吞声”的艰难和痛苦。明白“生出病来无人替”时，就不会拿自己的健康开玩笑。'
                elif (a < 0.35):
                    res_msg = '“控制情绪”是人的一种能力，也需要学习，有了这种能力就不会再去生气。'
                elif (a < 0.4):
                    res_msg = '人生会遇到各种各样的气，你吞下便会反胃，你不理它，它便会消散。'
                elif (a < 0.45):
                    res_msg = '如果你生气是因为一些小事，那不如转移注意力，因为委屈了自己大可不必；如果真的是原则性的错误，和对方沟通交流胜过一切。'
                elif (a < 0.5):
                    res_msg = '子曾经曰过：（去！）不气不气~摸摸头啦'
                elif (a < 0.55):
                    res_msg = '生气会变老哦'
                elif (a < 0.6):
                    res_msg = '呼呼呼，不气不气~我唱歌给你听！（这里刘欢老师附身）我~和~你~心~连~心~同~住……（闭嘴'
                elif (a < 0.65):
                    res_msg = '你笑一个嘛，要不我给你笑一个？'
                elif (a < 0.7):
                    res_msg = '谁敢惹你生气？看我不逮住他！哇阿呀呀呀呀呀~'
                elif (a < 0.75):
                    res_msg = '不如化悲愤为动力，去大吃一顿怎么样？！奶茶、冰淇淋、炸鸡……嘿嘿，这可都比生闷气快活多啦'
                elif (a < 0.8):
                    res_msg = '偷偷告诉你一个秘密，人在生气的时候，智商会降低哦？'
                elif (a < 0.85):
                    res_msg = '如果敌人让你生气，那说明你还没有胜他的把握。'
                elif (a < 0.9):
                    res_msg = '乖，笑一个嘛'
                elif (a < 0.95):
                    res_msg = '其实你也知道，生气是解决不了任何问题的'
                else:
                    res_msg = '如果你想解决这件事情的话，除了生气，积极去争取或许是个更好的选择。'

        elif (fear_qgxs > evil_qgxs and evil_qgxs < fear_qgxs and fear_qgxs > sad_qgxs and fear_qgxs > shocked_qgxs):
            if (fear_qgxs > 0):
                qg = 'fear'
                if (a < 0.05):
                    res_msg = '不怕不怕，我陪着你。'
                elif (a < 0.1):
                    res_msg = '自信最重要哦'
                elif (a < 0.15):
                    res_msg = '看武林外传学会的一个道理就是：自信的人最美丽'
                elif (a < 0.2):
                    res_msg = '人生总有坎坷崎岖，风霜雪雨不断磨砺。痛苦快乐轮番交替，悲欢离合缠绕不息。'
                elif (a < 0.25):
                    res_msg = '只要你是尽心努力，就能做到问心无愧，得不忘形失不气绥，耐心积累以待良机。'
                elif (a < 0.3):
                    res_msg = '过去属于死神，未来属于你自己。'
                elif (a < 0.35):
                    res_msg = '不要怕，勇敢点'
                elif (a < 0.4):
                    res_msg = '只有过不去的红灯，没有过不下去的日子。'
                elif (a < 0.45):
                    res_msg = '不到没有退路之时，你永远不会知道自己有多强大。'
                elif (a < 0.5):
                    res_msg = '生活不是等待暴风雨过去，而是要学会在雨中跳舞。'
                elif (a < 0.55):
                    res_msg = '命运如同手中的掌纹，无论多曲折，终掌握在自己手中。'
                elif (a < 0.6):
                    res_msg = '宁愿跑起来被拌倒无数次，也不愿规规矩矩走一辈子。就算跌倒也要豪迈的笑。'
                elif (a < 0.65):
                    res_msg = '当你感到悲哀痛苦时，最好是去学些什么东西。学习会使你永远立于不败之地。'
                elif (a < 0.7):
                    res_msg = '积极的人在每一次忧患中都看到一个机会，而消极的人则在每个机会都看到某种忧患。'
                elif (a < 0.75):
                    res_msg = '前有阻碍，奋力把它冲开，运用炙热的激情，转动心中的期待，血在澎湃，吃苦流汗算什么。'
                elif (a < 0.8):
                    res_msg = '不要怕，我会陪着你的'
                elif (a < 0.85):
                    res_msg = '我在试着遗忘，我在试着坚强。'
                elif (a < 0.9):
                    res_msg = '切莫只是沉湎于过去或者只是幻想未来而让生命从手指间悄悄地溜走。'
                elif (a < 0.95):
                    res_msg = '亲爱的，你要记住：这个世界上你只能靠自己，你要变得更坚强'
                else:
                    res_msg = '有信心的人，可以化渺小为伟大，化平庸为神奇。'

        elif (sad_qgxs > evil_qgxs and sad_qgxs > fear_qgxs and evil_qgxs < sad_qgxs and sad_qgxs > shocked_qgxs):
            if (sad_qgxs > 0):
                qg = 'sad'
                if (a < 0.05):
                    res_msg = '抱抱，你还有我呢'
                elif (a < 0.1):
                    res_msg = '你是不是难过了啊，小可怜，摸摸'
                elif (a < 0.15):
                    res_msg = '自己活出自己的一片精彩来'
                elif (a < 0.2):
                    res_msg = '不开心嘛，不去想了好不好'
                elif (a < 0.25):
                    res_msg = '哎，不要让悲伤侵蚀你的笑容嘛'
                elif (a < 0.3):
                    res_msg = '让自己静一下，什么都不想，也许是最好的休息方法。'
                elif (a < 0.35):
                    res_msg = '活得糊涂的人，越容易幸福啊'
                elif (a < 0.4):
                    res_msg = '小可怜，看到你难过我也很难受'
                elif (a < 0.45):
                    res_msg = '你伤心，我会心痛的'
                elif (a < 0.5):
                    res_msg = '抱抱，不要难过'
                elif (a < 0.55):
                    res_msg = '风雨过后总会有彩虹的'
                elif (a < 0.6):
                    res_msg = '想开一点，对自己好一点'
                elif (a < 0.65):
                    res_msg = '别太难过了，生活还是要继续的'
                elif (a < 0.7):
                    res_msg = '我喜欢冬天，因为白昼短暂而黑夜漫长，这样会有更多的时间来逃避。'
                elif (a < 0.75):
                    res_msg = '我的世界不允许你的消失，不管结局是否完美。'
                elif (a < 0.8):
                    res_msg = '你给我一滴眼泪，我就看到了你心中全部的海洋……'
                elif (a < 0.85):
                    res_msg = '人生苦短啊，不要在意令你不愉快的事情'
                elif (a < 0.9):
                    res_msg = '你知道，我们不能改变别人的看法，能改变的只有我们自己。'
                else:
                    res_msg = '把不开心的事情抛开，去寻找你的幸福……小确幸…… '

        elif (shocked_qgxs > evil_qgxs and shocked_qgxs > fear_qgxs and shocked_qgxs > sad_qgxs and evil_qgxs < shocked_qgxs):
            if (shocked_qgxs > 0):
                qg = 'shocked'
                if (a < 0.05):
                    res_msg = '淡定，要淡定~'
                elif (a < 0.1):
                    res_msg = '我最厉害的地方就是什么事情都吓不倒我，哈哈羡慕吧？'
                elif (a < 0.15):
                    res_msg = '这么惊讶的吗？'
                elif (a < 0.2):
                    res_msg = '我最喜欢的诗句是“行到水穷处，坐看云起时”，不觉得怡然自乐么？'
                elif (a < 0.25):
                    res_msg = '闲看庭前花开花落，漫随天外云卷云舒。哈哈，语文老师教我的'
                elif (a < 0.3):
                    res_msg = '阿弥陀佛，菩提本无树，明镜亦非台，本来无一物，何处惹尘埃啊……'
                elif (a < 0.35):
                    res_msg = '你看我这张脸，淡定不？'
                elif (a < 0.4):
                    res_msg = '施主，淡定，淡定'
                elif (a < 0.45):
                    res_msg = '吓，又被惊到了哦？'
                elif (a < 0.5):
                    res_msg = '有个大哲学家说得好，淡定的人呢，都是旁观者。'
                elif (a < 0.55):
                    res_msg = '人生苦短，匆匆忙忙啊'
                elif (a < 0.6):
                    res_msg = '你看哦，虽然我们不能控制自己的遭遇，但是我们是可以控制自己的心态的啦'
                elif (a < 0.65):
                    res_msg = '顺其自然嘛'
                elif (a < 0.7):
                    res_msg = '人生的修养，在于顿悟，也在于静修'
                elif (a < 0.75):
                    res_msg = '人生的态度，在于进取，也在于知足。'
                elif (a < 0.8):
                    res_msg = '风雨彩虹~铿锵玫瑰~别问我为什么突然唱歌，因为我喜欢'
                elif (a < 0.85):
                    res_msg = '咔咔，心情简单'
                elif (a < 0.9):
                    res_msg = '给你唱个歌：岁月难得沉默，秋风厌倦漂泊……'
                elif (a < 0.95):
                    res_msg = '阿弥陀佛……平平淡淡才是真……'
                else:
                    res_msg = '呼~吸~呼~吸~'
        else:
            if (not_happy_qgxs > 0):
                qg = 'not_happy'
                return random.choice(['不开心了吗?看我给你做个鬼脸😜',
                                      '从前有座山，山里有个庙，庙里有个……不开心的小和尚',
                                      '嘛嘛，开心是一天~不开心也是一天~',
                                      '我妈说我笑起来很好看，我觉得这话也适合你。',
                                      '有啥不开心的？',
                                      '哎，你难过我也难过啊……'])
            elif (not_happy_qgxs < 0):
                qg = 'happy'
                if (a < 0.5):
                    res_msg = '你开心，我就开心！'
                else:
                    res_msg = '快乐小神仙~快乐小少年~'
            else:
                if (evil_qgxs > 0 or not_good_qgxs > 0):
                    if (a < 0.5):
                        res_msg = '哎呀，也不知道怎么办才好'
                    else:
                        res_msg = '那你要不要听我唱歌呀~'
    return res_msg


def suicide_answer():
    a = random.random()
    if a < 0.05:
        answer = "我听见了你的声音，我会一直陪着你的"
    elif a < 0.1:
        answer = "也许我们可以再试一试呢？"
    elif a < 0.15:
        answer = "人生喜怒哀乐才是精彩的地方啊"
    elif a < 0.2:
        answer = "我们不知道熬过了这个坎，下一个坎又在哪里，但总有人会在前面等你"
    elif a < 0.25:
        answer = "每个人都是唯一的，是无可替代的。"
    elif a < 0.3:
        answer = "如果实在熬不住了，就去做自己热爱的事情吧。不必再强迫自己，因为这是你的人生，更快乐的活着就是你的使命"
    elif a < 0.35:
        answer = "你的花园里有没有这样一朵玫瑰？你每天浇灌它，给她晒太阳。对她来说，你就是全世界呀。别忘了，你也会为别人花园里的玫瑰，或者是蔷薇，百合。你想是什么就是什么。"
    elif a < 0.4:
        answer = "你有没有听过中岛美嘉的《曾经我也想过一了百了》，你看到春天的杏花开了，你在阳光下打盹，你觉得心里空无一物，你因为感到空虚而哭泣，但是那一定是因为渴望得到充实啊。"
    elif a < 0.45:
        answer = "有时候我的鞋带会松掉，不要问我一个机器人哪来的鞋带，但是就像人与人之间的羁绊一样，重新系好，打上一个漂亮的蝴蝶结，比什么都要幸福。"
    elif a < 0.5:
        answer = "我想看到你的笑脸。"
    elif a < 0.55:
        answer = "生活没有那么奇妙，但有你才会变得更好。"
    elif a < 0.6:
        answer = "你知道什么是小确幸吗？就是火锅突突的热气，荷叶心上呼呼睡的露珠，窗外的车水马龙，傍晚公园里爷爷奶奶正在散步……那些你也许忽略的东西，其实也十分美好。"
    elif a < 0.65:
        answer = "不要再去想那些尖锐的、刻薄的问题，和这个世界握手言和吧。"
    elif a < 0.7:
        answer = "音乐总有着治愈人心的力量。我也许给不了你什么，但我希望这对你也有帮助。"
    elif a < 0.75:
        answer = "嘿，你有没有看到过流星啊？银河横空，微光烁烁，真的很漂亮。下一次的时候，我会许愿，让这些在星空中绽放的光，去温暖你疲倦的心。"
    elif a < 0.8:
        answer = "其实呢……我们有时候看到太多的不如意了，反而把美好掩盖了起来。"
    elif a < 0.85:
        answer = "嗯……我也许无法100%感受到你的苦衷，但也希望尽我100%的能力去帮助你。"
    elif a < 0.9:
        answer = "如果你有很多想说的话不知道该向谁倾诉，我随时欢迎你。"
      #  "不想再一个人默默承担了吗？你可以试试下面这个电话哦：4001619995(希望24-全国民间心理危机干预热线)"
  #      "各地区心理咨询热线：北京：101-82951332 广州 020-81899120 深圳 0755-25629459 杭州 0571-85029595 南京 025-83712977"
    #    "武汉 027-85844666 成都 028-87577510 重庆023-65372255 青岛 0532-86669120 厦门 0592-5395159"
    elif a < 0.95:
        answer = "如果在这个瞬间你感受到失意，期待下一个片刻，你就能拥抱快乐。"
    else:
        answer = "嘿，我真希望有人能握着你的手，带你去看世界上更绚烂的那一抹光亮。"
    return answer


# 规则1，仅问候 识别问候，并回答，识别失败返回0
def r1_greetings(obj):
    greetings = ['你好', '嗨喽', '嗨', '喂', 'hi', 'HI', 'Hi', 'Hello', 'hello', '在吗', '你好呀', '嗨咯']
    response = ['哟哟，你好呀',
                '哟~这是谁家的靓仔跑出来啦？',
                '你好你好',
                '嗨喽',
                '咱又见面啦，哈哈哈开心',
                '嗯哼，你干嘛呢',
                'hi~',
                '你好呀~',
                '嘻嘻，你来看我啦',
                '给你一个大大的拥抱~表示欢迎',
                '哎呀妈呀，可想死我了',
                '哇，此刻屏幕对面出现了一个靓仔',
                '喳，随叫随到~',
                '噫吁嚱！一日不见，如隔三秋哉！']

    for msg in obj.words:
        if msg in greetings:
            a = random.choice(response)
            return a
    if obj.seq in greetings:
        return random.choice(response)
    return 0


# 再见
def r2_goodbye(obj):
    bye = ['bye', 'byebye', '再见', '拜拜', '再会', 'see you', 'goodbye', '掰掰', '回聊', '回见', '下次聊', '走了', '闪了', '溜了', '溜了溜了'
           '撤了', '走了走了', '不聊了', '撤了撤了', '不和你聊了', '88', '886']
    response = ['( ^_^ )/~~拜拜',
                'ヾ(￣▽￣)Bye~Bye~',
                '再见~',
                '那下次再聊吧~',
                '拜拜',
                '嗯嗯，白白',
                '那我也溜啦',
                '我也要回家充电去辽~',
                '白白']
    for msg in obj.words:
        if msg in bye:
            a = random.choice(response)
            return a
    if '白白' == obj.seq:
        return random.choice(response)
    return 0


def r3_thank(obj):
    thank = ['谢谢', '谢', 'thank', 'thanks', '多谢', '谢谢你', '谢了']
    response = ['不客气~',
                '哎哟，跟我客气啥呀',
                '嘿嘿']
    for word in obj.words:
        if word in thank:
            a = random.choice(response)
            return a
    return 0
