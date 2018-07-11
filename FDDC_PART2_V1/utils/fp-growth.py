import pyfpgrowth
import re
from FDDC_PART2_V1.preprocess.hetong.Trainfile_HT_ALL_NER_TEXT import getHeTongUnion, levelText_without_table, dz_trainpath, dz_htmlpath
from FDDC_PART2_V1.nlp.tokenize.cws import ltp_tokenize

'''
transactions = [[1, 2, 5],
                [2, 4],
                [2, 3],
                [1, 2, 4],
                [1, 3],
                [2, 3],
                [1, 3],
                [1, 2, 3, 5],
                [1, 2, 3]]

patterns = pyfpgrowth.find_frequent_patterns(transactions, 2)
rules = pyfpgrowth.generate_association_rules(patterns, 0.7)
print(patterns)
'''


# print(patterns)
# print(rules)


# 寻找实体所在前缀的分词事务，以供规则挖掘
def find_prefix_trans(before=0, limit=-5):
    hetongs = getHeTongUnion(dz_trainpath)
    transactions = {}
    for id in hetongs.keys():
        hts = hetongs[id]
        htmlpath = dz_htmlpath + id + '.html'
        sentences = levelText_without_table(htmlpath)
        for sid in range(len(sentences)):
            sentence = sentences[sid]
            beforetext = ''
            for i in range(sid - before, sid):
                if i >= 0:
                    beforetext += sentences[i]
            context = beforetext + sentence

            val = hts[0].yifang
            for i in range(1, len(hts)):
                val += ('|' + hts[i].yifang)
            label = 'YF'

            cuts = cut_text_by_val(context, val, hts)
            if len(cuts) > 0:
                for cut in cuts:
                    tokens = ltp_tokenize(cut)[limit:]  # 向前找限制N个词
                    # tokens.append(label)
                    if len(tokens) > 0:
                        transactions[cut] = tokens

    return transactions


def cut_text_by_val(text, val, hts, limit=0):
    iters = re.finditer(val, text, re.I)
    cuts = []
    previous = 0
    for iter in iters:
        begin, end = iter.span()  # 返回每个匹配坐标
        t = text[previous:begin]
        # t = removeall_obj(t, hts)
        if len(t) > limit:
            cuts.append(t)
        previous = end
    return cuts


def removeall_obj(text, hts):
    for ht in hts:
        text = text.replace(ht.yifang, '')
        text = text.replace(ht.jiafang, '')
        text = text.replace(ht.xiangmu, '')
        text = text.replace(ht.hetong, '')
        text = text.replace(ht.amount_u, '')
        text = text.replace(ht.amount_d, '')
        for lh in ht.lianhe.split('、'):
            text = text.replace(lh, '')

    return text


transactions = find_prefix_trans(before=0)
for k, v in transactions.items():
    print(k, ' -> ', v)
# patterns = pyfpgrowth.find_frequent_patterns(transactions.values(), 10)
# # rules = pyfpgrowth.generate_association_rules(patterns, 0.1)
# list = sorted(patterns.items(), key=lambda d: d[1], reverse=True)
# for it in list:
#     print(it)
