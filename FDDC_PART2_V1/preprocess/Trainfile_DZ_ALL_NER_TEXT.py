import re
from decimal import Decimal

from bs4 import BeautifulSoup

from FDDC_PART2.preprocessing.QANetTrainFile import getDingZengUnion
from FDDC_PART2.preprocessing.normalizer import norm_dz
from FDDC_PART2_V1.nlp.tokenize.cws import ltp_tokenize_distinct
import FDDC_PART2_V1.rules.dingzengPackage as package

# 公告id,增发对象,发行方式,增发数量,增发金额,锁定期,认购方式
dataroot = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/nlp/NER_IDCNN_CRF/data/'
dz_trainpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/dingzeng.train'
dz_htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/html/'

reg_isnum = '\d+(\.\d+)?'
pattern_isnum = re.compile(reg_isnum)


def showText(before=1):
    dingzengs = getDingZengUnion(dz_trainpath)
    dx_dict = {}
    sl_dict = {}
    je_dict = {}
    for id in dingzengs.keys():
        dzs = dingzengs[id]
        htmlpath = dz_htmlpath + id + '.html'
        sentences = levelText_without_table(htmlpath)
        for sid in range(len(sentences)):
            sentence = sentences[sid]
            beforetext = ''
            for i in range(sid - before, sid):
                if i >= 0:
                    beforetext += sentences[i]
            context = beforetext + sentence
            ywset = ltp_tokenize_distinct(context)
            tag_arr = ['O'] * len(sentence)
            isMask = False
            for dz in dzs:
                if mask_contract_field(sentence, dz.duixiang, tag_arr, 'DX', dz):
                    setCount(dx_dict, ywset, id)
                    isMask = True
                if mask_contract_field(sentence, dz.shuliang, tag_arr, 'SL', dz):
                    setCount(sl_dict, ywset, id)
                    isMask = True
                if mask_contract_field(sentence, dz.jine, tag_arr, 'JE', dz):
                    setCount(je_dict, ywset, id)
                    isMask = True
            if isMask:
                print('sid=' + str(sid) + ' sentence:' + sentence)
                # print('beforetext:' + beforetext)
        print('--------------------------------')

    guolv = {k: v for k, v in dx_dict.items() if len(v) > 9}
    paixu = sorted(guolv.items(), key=lambda d: len(d[1]), reverse=True)
    print('--------------------------------------------------------------------------------------------------------')
    for px in paixu:
        print(px[0] + '\t' + str(px[1]))

    guolv = {k: v for k, v in sl_dict.items() if len(v) > 9}
    paixu = sorted(guolv.items(), key=lambda d: len(d[1]), reverse=True)
    print('--------------------------------------------------------------------------------------------------------')
    for px in paixu:
        print(px[0] + '\t' + str(px[1]))

    guolv = {k: v for k, v in je_dict.items() if len(v) > 9}
    paixu = sorted(guolv.items(), key=lambda d: len(d[1]), reverse=True)
    print('--------------------------------------------------------------------------------------------------------')
    for px in paixu:
        print(px[0] + '\t' + str(px[1]))


def maketrain(before=0):
    rank = 6
    dz_train = open(dataroot + 'dz_all_text.train', 'a+')
    dz_dev = open(dataroot + 'dz_all_text.dev', 'a+')
    dingzengs = getDingZengUnion(dz_trainpath)
    for id in dingzengs.keys():
        mod = int(id) % rank
        if mod == 0:
            makefile = dz_dev
        else:
            makefile = dz_train
        dzs = dingzengs[id]
        htmlpath = dz_htmlpath + id + '.html'
        sentences = levelText_without_table(htmlpath)
        for sid in range(len(sentences)):
            sentence = sentences[sid]
            beforetext = ''
            for i in range(sid - before, sid):
                if i >= 0:
                    beforetext += sentences[i]
            context = beforetext + sentence
            context = context.replace('十二个月', '12个月')
            context = context.replace('三十六个月', '12个月')
            tag_arr = ['O'] * len(context)
            isMask = False
            for dz in dzs:
                if package.reg_dx_table(context) and mask_contract_field(context, dz.duixiang, tag_arr, 'DX', dz, False):
                    isMask = True
                if package.reg_sl_table(context) and mask_contract_field(context, dz.shuliang, tag_arr, 'SL', dz, True):
                    isMask = True
                if package.reg_je_table(context) and mask_contract_field(context, dz.jine, tag_arr, 'JE', dz, True):
                    isMask = True
                if package.reg_sd_table(context) and mask_contract_field(context, dz.suoding, tag_arr, 'SD', dz, False):
                    isMask = True
                if package.reg_rg_table(context) and mask_contract_field(context, dz.rengou, tag_arr, 'RG', dz, False):
                    isMask = True
            if isMask:
                for i in range(len(context)):
                    makefile.write(context[i] + ' ' + tag_arr[i] + '\n')
                makefile.write('\n')
        print('--------------------------------')
        for dz in dzs:
            dz.desc()


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
            p_title = norm_dz(p_title)
            if len(p_title) > 0:
                sents_arr.append(p_title)
        for content in paragraph.find_all('div', type='content'):
            c_title = content.attrs.get('title')
            if c_title is not None:
                c_title = norm_dz(c_title)
                if len(c_title) > 0:
                    sents_arr.append(c_title)
            tables = content.find_all('table')
            # 假设训练数据中，text和table不同时存在于同一content内
            if len(tables) == 0:
                sentences = content.get_text().split('。')
                for sentence in sentences:
                    # 合并，英语怎么处理？
                    sen = norm_dz(sentence)
                    if len(sen) > 0:
                        sents_arr.append(sen + "。")
    return sents_arr


def mask_contract_field(line_source, val, tag_arr, label, dingzeng, isnum):
    isMask = False
    if val != 'fddcUndefined':
        val = val.replace('(', '\(')
        val = val.replace(')', '\)')
        val = val.replace('[', '\[')
        val = val.replace(']', '\]')
        if isnum:
            iters = pattern_isnum.finditer(line_source)
            for iter in iters:
                begin, end = iter.span()  # 返回每个匹配坐标
                if iter.group() == val:
                    dingzeng.setStatus(label)
                    tag_arr[begin] = 'B-' + label
                    for index in range(begin + 1, end):
                        tag_arr[index] = 'I-' + label
                    isMask = True
        else:
            iters = re.finditer(val, line_source, re.I)
            for iter in iters:
                begin, end = iter.span()  # 返回每个匹配坐标
                dingzeng.setStatus(label)
                tag_arr[begin] = 'B-' + label
                for index in range(begin + 1, end):
                    tag_arr[index] = 'I-' + label
                isMask = True

    return isMask


maketrain()
# showText()
