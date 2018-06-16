from pyltp import Segmentor
import re
import spacy
from stanfordcorenlp import StanfordCoreNLP

nlp = spacy.blank("zh")

corenlp = StanfordCoreNLP(r'/home/utopia/corpus/stanford-corenlp-full-2018-02-27', lang='zh')

cws_model_path = '/home/utopia/corpus/ltp_data_v3.4.0/cws.model'  # ltp模型目录的路径
segmentor = Segmentor()  # 初始化实例
segmentor.load(cws_model_path)  # 加载模型

sentence = '本公司于 2014 年 5 月 21 日接到公司控股股东中国南方工业集团' \
           '公司(以下简称“南方集团”)通知:南方集团于 2014 年 5 月 20 日' \
           '通过上海证券交易所大宗交易系统减持本公司股份 12,000,000 股,约' \
           '占本公司总股本的 1.75%。本次减持前,南方集团持有本公司股份 185,' \
           '566,173.00 股,占本公司总股本的 27.00%;本次减持后,南方集团持' \
           '有本公司股份173,566,173.00 股,占本公司总股本的 25.25%。本次' \
           '减持严格遵守中国证监会、上海证券交易所等相关法律、法规及业务规则的规定。特此公告。'
sentence = re.sub('\s+', '', sentence)


def word_tokenize(sent):
    doc = nlp(sent)
    return [token.text for token in doc]


print(word_tokenize(sentence))

print(corenlp.word_tokenize(sentence))
# print(corenlp.pos_tag(sentence))
# print(corenlp.ner(sentence))
# print(corenlp.parse(sentence))
# print(corenlp.dependency_parse(sentence))

# 结论：jieba挺好

words = segmentor.segment(sentence)  # 分词
words_list = list(words)
print(words_list)
segmentor.release()  # 释放模型
