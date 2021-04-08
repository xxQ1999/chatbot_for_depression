import os
import pandas as pd
import random
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import SementicRoleLabeller


LTP_DATA_DIR = 'ltp\ltp_data'

def get_model_path(kind):
    LTP_DATA_DIR = 'ltp\ltp_data'
    cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型
    pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注
    ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别
    parser_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 句法分析
    labeller_model_path = os.path.join(LTP_DATA_DIR, 'pisrl_win.model')
    if kind == 1:
        return cws_model_path       # 分词模型
    elif kind == 2:
        return pos_model_path       # 词性标注
    elif kind == 3:
        return ner_model_path        # 命名实体识别
    elif kind == 4:
        return parser_model_path       # 句法分析


def word_spliter(sentence):
    segmentor = Segmentor()             # 初始化实例
    cws_model_path = get_model_path(1)
    segmentor.load(cws_model_path)  # 加载模型
    words = segmentor.segment(sentence)
    yield [word for word in words]
    segmentor.release()
   # return words


def posttagger(sentence):
    words = word_spliter(sentence)
    pos_model_path = get_model_path(2)
    postagger = Postagger()  # 初始化实例
    postagger.load(pos_model_path)  # 加载模型
    for word in words:
        postags = postagger.postag(word)
        yield word, postags
    postagger.release()


def analysis_sentence(sentence):
    pw_combine = posttagger(sentence)
    par_model_path = get_model_path(4)
    parser = Parser()
    parser.load(par_model_path)
    for word, postag in pw_combine:
        arcs = parser.parse(word, postag)  # return list(acr.head,arc.relation)
        head_num_list = [arc.head for arc in arcs]
        head_list = ['Root' if num == 0 else word[num-1] for num in head_num_list]
        relation_list = [arc.relation for arc in arcs]

        for i in range(len(word)):
            print(relation_list[i] + '(' + word[i] + ',' + head_list[i] + ')')

        yield word, head_num_list, postag, relation_list
    parser.release()

if __name__ == "__main__":
    sentence = "我担心考试过不了"
    generator = analysis_sentence(sentence)
    for word, head_num_list, postag, relation_list in generator:
        print()

