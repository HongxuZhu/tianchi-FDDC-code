import re

from bs4 import BeautifulSoup

import FDDC_PART2_V1.rules.dingzengPackage as package
from FDDC_PART2.preprocessing.entity import Contract
from FDDC_PART2.preprocessing.normalizer import norm_ht

# 公告id,增发对象,发行方式,增发数量,增发金额,锁定期,认购方式
dataroot = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/nlp/NER_IDCNN_CRF/data/'
dz_trainpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/重大合同/hetong.train'
dz_htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/重大合同/html/'

reg_isnum = '\d+(\.\d+)?'
pattern_isnum = re.compile(reg_isnum)


def getHeTongUnion(trainpath):
    cons = {}
    with open(trainpath, 'r') as file:
        for line in file:
            line = line[0:len(line) - 1]
            con = Contract(line)
            dzarray = cons.get(con.id)
            if dzarray is not None:
                cons[con.id].append(con)
            else:
                cons[con.id] = [con]
    return cons


def showText(before=0):
    hetongs = getHeTongUnion(dz_trainpath)
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
            tag_arr = ['O'] * len(sentence)
            isMask = False
            for ht in hts:
                if mask_contract_field(sentence, ht.jiafang, tag_arr, 'JF', ht, False):
                    isMask = True
                if mask_contract_field(sentence, ht.yifang, tag_arr, 'YF', ht, False):
                    isMask = True
                if mask_contract_field(sentence, ht.xiangmu, tag_arr, 'XM', ht, False):
                    isMask = True
                if mask_contract_field(sentence, ht.hetong, tag_arr, 'HT', ht, False):
                    isMask = True
                if mask_contract_field(sentence, ht.amount_u, tag_arr, 'AU', ht, True):
                    isMask = True
                if mask_contract_field(sentence, ht.amount_d, tag_arr, 'AD', ht, True):
                    isMask = True
                lhs = ht.lianhe.split('、')
                for lh in lhs:
                    mask_contract_field(sentence, lh, tag_arr, 'LH', ht, False)
            if isMask:
                pass

        for ht in hts:
            ht.desc()


def discoverText(before=0):
    hetongs = getHeTongUnion(dz_trainpath)
    dx_dict = {}
    sl_dict = {}
    je_dict = {}
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
            # ywset = jieba_tokenize_distinct(context)
            tag_arr = ['O'] * len(sentence)
            isMask = False
            for ht in hts:
                if mask_contract_field(sentence, ht.jiafang, tag_arr, 'JF', ht, False):
                    # setCount(dx_dict, ywset, id)
                    isMask = True
                if mask_contract_field(sentence, ht.yifang, tag_arr, 'YF', ht, False):
                    isMask = True
                if mask_contract_field(sentence, ht.xiangmu, tag_arr, 'XM', ht, False):
                    isMask = True
                if mask_contract_field(sentence, ht.hetong, tag_arr, 'HT', ht, False):
                    isMask = True
                if mask_contract_field(sentence, ht.amount_u, tag_arr, 'AU', ht, True):
                    isMask = True
                if mask_contract_field(sentence, ht.amount_d, tag_arr, 'AD', ht, True):
                    isMask = True
                lhs = ht.lianhe.split('、')
                for lh in lhs:
                    mask_contract_field(sentence, lh, tag_arr, 'LH', ht, False)
            if isMask:
                pass
                # print('sid=' + str(sid) + ' sentence:' + sentence)
                # print('beforetext:' + beforetext)

        for ht in hts:
            ht.desc()

    # guolv = {k: v for k, v in dx_dict.items() if len(v) > 9}
    # paixu = sorted(guolv.items(), key=lambda d: len(d[1]), reverse=True)
    # print('--------------------------------------------------------------------------------------------------------')
    # for px in paixu:
    #     print(px[0] + '\t' + str(px[1]))
    #
    # guolv = {k: v for k, v in sl_dict.items() if len(v) > 9}
    # paixu = sorted(guolv.items(), key=lambda d: len(d[1]), reverse=True)
    # print('--------------------------------------------------------------------------------------------------------')
    # for px in paixu:
    #     print(px[0] + '\t' + str(px[1]))
    #
    # guolv = {k: v for k, v in je_dict.items() if len(v) > 9}
    # paixu = sorted(guolv.items(), key=lambda d: len(d[1]), reverse=True)
    # print('--------------------------------------------------------------------------------------------------------')
    # for px in paixu:
    #     print(px[0] + '\t' + str(px[1]))


def maketrain(before=0):
    rank = 6
    ht_train = open(dataroot + 'ht_all_text.train', 'a+')
    ht_dev = open(dataroot + 'ht_all_text.dev', 'a+')
    hetongs = getHeTongUnion(dz_trainpath)
    for id in hetongs.keys():
        mod = int(id) % rank
        if mod == 0:
            makefile = ht_dev
        else:
            makefile = ht_train
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
            tag_arr = ['O'] * len(context)
            isMask = False
            for ht in hts:
                if mask_contract_field(context, ht.jiafang, tag_arr, 'JF', ht, False):
                    isMask = True
                if mask_contract_field(context, ht.yifang, tag_arr, 'YF', ht, False):
                    isMask = True
                if mask_contract_field(context, ht.xiangmu, tag_arr, 'XM', ht, False):
                    isMask = True
                if mask_contract_field(context, ht.hetong, tag_arr, 'HT', ht, False):
                    isMask = True
                if mask_contract_field(context, ht.amount_u, tag_arr, 'AU', ht, True):
                    isMask = True
                if mask_contract_field(context, ht.amount_d, tag_arr, 'AD', ht, True):
                    isMask = True
                lhs = ht.lianhe.split('、')
                for lh in lhs:
                    mask_contract_field(context, lh, tag_arr, 'LH', ht, False)
            if isMask:
                for i in range(len(context)):
                    makefile.write(context[i] + ' ' + tag_arr[i] + '\n')
                makefile.write('\n')

        for ht in hts:
            ht.desc()


def setCount(ywdict, ywset, id):
    for word in ywset:
        val = ywdict.get(word)
        if val is None:
            newset = set()
            newset.add(id)
            ywdict[word] = newset
        else:
            val.add(id)


def levelText_without_table(htmlpath):
    soup = BeautifulSoup(open(htmlpath), 'lxml')
    sents_arr = []
    for paragraph in soup.find_all('div', type='paragraph'):
        p_title = paragraph.attrs.get('title')
        if p_title is not None:
            p_title = norm_ht(p_title)
            if len(p_title) > 0:
                sents_arr.append(p_title)
        for content in paragraph.find_all('div', type='content'):
            c_title = content.attrs.get('title')
            if c_title is not None:
                c_title = norm_ht(c_title)
                if len(c_title) > 0:
                    sents_arr.append(c_title)
            tables = content.find_all('table')
            # 假设训练数据中，text和table不同时存在于同一content内
            if len(tables) == 0:
                sentences = content.get_text().split('。')
                for sentence in sentences:
                    # 合并，英语怎么处理？
                    sen = norm_ht(sentence)
                    if len(sen) > 0:
                        sents_arr.append(sen + "。")
    return sents_arr


def mask_contract_field(line_source, val, tag_arr, label, obj, isnum):
    isMask = False
    if val != 'fddcUndefined':
        val = val.replace('(', '\(')
        val = val.replace(')', '\)')
        val = val.replace('[', '\[')
        val = val.replace(']', '\]')
        val = val.replace('+', '\+')
        # val = val.replace('.', '\.')
        if isnum:
            iters = pattern_isnum.finditer(line_source)
            for iter in iters:
                begin, end = iter.span()  # 返回每个匹配坐标
                if iter.group() == val:
                    obj.setStatus(label)
                    tag_arr[begin] = 'B-' + label
                    for index in range(begin + 1, end):
                        tag_arr[index] = 'I-' + label
                    isMask = True
        else:
            iters = re.finditer(val, line_source, re.I)
            for iter in iters:
                begin, end = iter.span()  # 返回每个匹配坐标
                obj.setStatus(label)
                tag_arr[begin] = 'B-' + label
                for index in range(begin + 1, end):
                    tag_arr[index] = 'I-' + label
                isMask = True

    return isMask


# maketrain()
showText()
