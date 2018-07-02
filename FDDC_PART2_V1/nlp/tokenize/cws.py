from pyltp import Segmentor
import jieba
import spacy
from pyhanlp import *
from stanfordcorenlp import StanfordCoreNLP

nlp = spacy.blank("zh")

jieba.initialize()

# corenlp = StanfordCoreNLP(r'/home/utopia/corpus/stanford-corenlp-full-2018-02-27', lang='zh')


cws_model_path = '/home/utopia/corpus/ltp_data_v3.4.0/cws.model'  # ltp模型目录的路径
segmentor = Segmentor()  # 初始化实例
segmentor.load(cws_model_path)  # 加载模型


def jieba_tokenize(sent):
    words = jieba.cut(sent)
    return list(words)


def jieba_tokenize_distinct(sent):
    words = jieba.cut(sent)
    return set(list(words))


def hanlp_tokenize(sent):
    return [term.word for term in HanLP.segment(sent)]


# def corenlp_tokenize(sent):
#     return corenlp.word_tokenize(sent)

def ltp_tokenize(sent):
    words = segmentor.segment(sent)  # 分词
    words_list = list(words)
    return words_list


def ltp_tokenize_distinct(sent):
    words = segmentor.segment(sent)  # 分词
    words_list = list(words)
    return set(words_list)
