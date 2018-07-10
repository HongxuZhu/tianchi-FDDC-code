import re

from bs4 import BeautifulSoup

from FDDC_PART2_V1.rules.hetongPackage import filter_ht, filter_lh, filter_xm
from FDDC_PART2.preprocessing.entity import Contract
from FDDC_PART2.preprocessing.normalizer import norm_ht
from FDDC_PART2_V1.nlp.tokenize.cws import ltp_pos_v_distinct, jieba_tokenize

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
                if mask_contract_field_char(sentence, ht.jiafang, tag_arr, 'JF', ht, False):
                    isMask = True
                if mask_contract_field_char(sentence, ht.yifang, tag_arr, 'YF', ht, False):
                    isMask = True
                if mask_contract_field_char(sentence, ht.xiangmu, tag_arr, 'XM', ht, False):
                    isMask = True
                if mask_contract_field_char(sentence, ht.hetong, tag_arr, 'HT', ht, False):
                    isMask = True
                if mask_contract_field_char(sentence, ht.amount_u, tag_arr, 'AU', ht, True):
                    isMask = True
                if mask_contract_field_char(sentence, ht.amount_d, tag_arr, 'AD', ht, True):
                    isMask = True
                lhs = ht.lianhe.split('、')
                for lh in lhs:
                    if mask_contract_field_char(sentence, lh, tag_arr, 'LH', ht, False):
                        isMask = True
            if isMask:
                pass

        for ht in hts:
            ht.desc()


# 探索关键词
def discoverText(before=0):
    hetongs = getHeTongUnion(dz_trainpath)
    dx_dict = {}
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
                '''
                setCount(dx_dict, ywset, id) 打开哪个注释，则看哪个字段的关键词
                '''
                if mask_contract_field_char(sentence, ht.jiafang, tag_arr, 'JF', ht, False):
                    prefix = sentence[0:sentence.find(ht.jiafang)]
                    ywset = ltp_pos_v_distinct(prefix)
                    setCount(dx_dict, ywset, id)
                    isMask = True
                if mask_contract_field_char(sentence, ht.yifang, tag_arr, 'YF', ht, False):
                    # setCount(dx_dict, ywset, id)
                    isMask = True
                if mask_contract_field_char(sentence, ht.xiangmu, tag_arr, 'XM', ht, False):
                    # setCount(dx_dict, ywset, id)
                    isMask = True
                if mask_contract_field_char(sentence, ht.hetong, tag_arr, 'HT', ht, False):
                    # setCount(dx_dict, ywset, id)
                    isMask = True
                if mask_contract_field_char(sentence, ht.amount_u, tag_arr, 'AU', ht, True):
                    # setCount(dx_dict, ywset, id)
                    isMask = True
                if mask_contract_field_char(sentence, ht.amount_d, tag_arr, 'AD', ht, True):
                    # setCount(dx_dict, ywset, id)
                    isMask = True
                lhs = ht.lianhe.split('、')
                for lh in lhs:
                    if mask_contract_field_char(sentence, lh, tag_arr, 'LH', ht, False):
                        # prefix = sentence[0:sentence.find(lh)]
                        # ywset = ltp_pos_v_distinct(prefix)
                        # setCount(dx_dict, ywset, id)
                        isMask = True

    guolv = {k: len(v) for k, v in dx_dict.items() if len(v) > 9}
    paixu = sorted(guolv.items(), key=lambda d: d[1], reverse=True)
    print('--------------------------------------------------------------------------------------------------------')
    for px in paixu:
        print(px[0] + '\t' + str(px[1]))


def maketrain_char(before=0):
    rank = 6
    ht_train = open(dataroot + 'ht_all_text.train', 'a+')
    ht_dev = open(dataroot + 'ht_all_text.dev', 'a+')
    cls_train = open('ht_cls_text.train', 'a+')
    cls_dev = open('ht_cls_text.dev', 'a+')
    hetongs = getHeTongUnion(dz_trainpath)
    for id in hetongs.keys():
        mod = int(id) % rank
        if mod == 0:
            nerfile = ht_dev
            clsfile = cls_dev
        else:
            nerfile = ht_train
            clsfile = cls_train
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
            labels = set()
            tag_arr = ['O'] * len(context)
            isMask = False
            for ht in hts:
                if mask_contract_field_char(context, ht.jiafang, tag_arr, 'JF', ht, False):
                    labels.add('__label__jf')
                    isMask = True
                if mask_contract_field_char(context, ht.yifang, tag_arr, 'YF', ht, False):
                    labels.add('__label__yf')
                    isMask = True
                if mask_contract_field_char(context, ht.xiangmu, tag_arr, 'XM', ht, False):
                    labels.add('__label__xm')
                    isMask = True
                if mask_contract_field_char(context, ht.hetong, tag_arr, 'HT', ht, False):
                    labels.add('__label__ht')
                    isMask = True
                if mask_contract_field_char(context, ht.amount_u, tag_arr, 'AU', ht, True):
                    labels.add('__label__amount')
                    isMask = True
                if mask_contract_field_char(context, ht.amount_d, tag_arr, 'AD', ht, True):
                    labels.add('__label__amount')
                    isMask = True
                lhs = ht.lianhe.split('、')

                # if filter_lh(context):
                for lh in lhs:
                    if mask_contract_field_char(context, lh, tag_arr, 'LH', ht, False):
                        labels.add('__label__lht')
                        isMask = True
            if True:
                for i in range(len(context)):
                    nerfile.write(context[i] + ' ' + tag_arr[i] + '\n')
                nerfile.write('\n')
            else:
                labels.add('__label__nothing')

            toline = ' '.join(labels) + ' ' + ' '.join(jieba_tokenize(context)) + '\n'
            clsfile.write(toline)

        for ht in hts:
            ht.desc()


def maketrain_word(before=0):
    rank = 7
    ht_train = open(dataroot + 'ht_all_text_word.train', 'a+')
    ht_dev = open(dataroot + 'ht_all_text_word.dev', 'a+')
    ht_test = open(dataroot + 'ht_all_text_word.test', 'a+')
    cls_train = open('ht_cls_text_word.train', 'a+')
    cls_dev = open('ht_cls_text_word.dev', 'a+')
    hetongs = getHeTongUnion(dz_trainpath)
    for id in hetongs.keys():
        mod = int(id) % rank
        if mod == 0:
            nerfile = ht_dev
            clsfile = cls_dev
        elif mod == 1:
            nerfile = ht_test
            clsfile = cls_dev
        else:
            nerfile = ht_train
            clsfile = cls_train
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
            cws_cut_cent = jieba_tokenize(context)
            labels = set()
            tag_arr = ['O'] * len(cws_cut_cent)
            isMask = False
            for ht in hts:
                if mask_contract_field_word(context, cws_cut_cent, ht.jiafang, tag_arr, 'JF', ht, False):
                    labels.add('__label__jf')
                    isMask = True
                if mask_contract_field_word(context, cws_cut_cent, ht.yifang, tag_arr, 'YF', ht, False):
                    labels.add('__label__yf')
                    isMask = True
                if mask_contract_field_word(context, cws_cut_cent, ht.xiangmu, tag_arr, 'XM', ht, False):
                    labels.add('__label__xm')
                    isMask = True
                if mask_contract_field_word(context, cws_cut_cent, ht.hetong, tag_arr, 'HT', ht, False):
                    labels.add('__label__ht')
                    isMask = True
                if mask_contract_field_word(context, cws_cut_cent, ht.amount_u, tag_arr, 'AU', ht, True):
                    labels.add('__label__amount')
                    isMask = True
                if mask_contract_field_word(context, cws_cut_cent, ht.amount_d, tag_arr, 'AD', ht, True):
                    labels.add('__label__amount')
                    isMask = True
                lhs = ht.lianhe.split('、')

                # if filter_lh(context):
                for lh in lhs:
                    if mask_contract_field_word(context, cws_cut_cent, lh, tag_arr, 'LH', ht, False):
                        labels.add('__label__lht')
                        isMask = True
            if True:
                # for i in range(len(context)):
                #     # nerfile.write(str(i + 1) + '\t' + context[i] + '\t' + tag_arr[i] + '\n')
                #     nerfile.write(context[i] + ' ' + tag_arr[i] + '\n')
                # nerfile.write('\n')

                for i in range(len(cws_cut_cent)):
                    nerfile.write(str(i + 1) + '\t' + cws_cut_cent[i] + '\t' + tag_arr[i] + '\n')
                nerfile.write('\n')
            else:
                labels.add('__label__nothing')

            # toline = ' '.join(labels) + ' ' + ' '.join(jieba_tokenize(context)) + '\n'
            # clsfile.write(toline)

        for ht in hts:
            ht.desc()


def maketrain_word_debug(id, before=0):
    hetongs = getHeTongUnion(dz_trainpath)
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
        cws_cut_cent = jieba_tokenize(context)
        labels = set()
        tag_arr = ['O'] * len(cws_cut_cent)
        for ht in hts:
            if mask_contract_field_word(context, cws_cut_cent, ht.jiafang, tag_arr, 'JF', ht, False):
                labels.add('__label__jf')
            if mask_contract_field_word(context, cws_cut_cent, ht.yifang, tag_arr, 'YF', ht, False):
                labels.add('__label__yf')
            if mask_contract_field_word(context, cws_cut_cent, ht.xiangmu, tag_arr, 'XM', ht, False):
                labels.add('__label__xm')
            if mask_contract_field_word(context, cws_cut_cent, ht.hetong, tag_arr, 'HT', ht, False):
                labels.add('__label__ht')
            if mask_contract_field_word(context, cws_cut_cent, ht.amount_u, tag_arr, 'AU', ht, True):
                labels.add('__label__amount')
            if mask_contract_field_word(context, cws_cut_cent, ht.amount_d, tag_arr, 'AD', ht, True):
                labels.add('__label__amount')
            lhs = ht.lianhe.split('、')

            for lh in lhs:
                if mask_contract_field_word(context, cws_cut_cent, lh, tag_arr, 'LH', ht, False):
                    labels.add('__label__lht')

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


# def levelText_without_table(htmlpath):
#     soup = BeautifulSoup(open(htmlpath), 'lxml')
#     sents_arr = []
#     for paragraph in soup.find_all('div', type='paragraph'):
#         p_title = paragraph.attrs.get('title')
#         if p_title is not None:
#             p_title = norm_ht(p_title)
#             if len(p_title) > 0:
#                 sents_arr.append(p_title + "。")
#         sents_content = ''
#         for content in paragraph.find_all('div', type='content'):
#             c_title = content.attrs.get('title')
#             if c_title is not None:
#                 if len(c_title) > 0:
#                     sents_content += (c_title + "。")
#             tables = content.find_all('table')
#             if len(tables) == 0:
#                 sents_content += content.get_text()
#         sents_content = norm_ht(sents_content)
#         sentences = sents_content.split('。')
#         for sentence in sentences:
#             sents_arr.append(sentence + "。")
#     return sents_arr


def mask_contract_field_char(line_source, val, tag_arr, label, obj, isnum):
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
                    ner_label = label
                    # if ner_label in ['JF', 'YF', 'LH']:
                    #     ner_label = 'ORG'
                    tag_arr[begin] = 'B-' + ner_label
                    for index in range(begin + 1, end):
                        tag_arr[index] = 'I-' + ner_label
                    isMask = True
        else:
            iters = re.finditer(val, line_source, re.I)
            for iter in iters:
                begin, end = iter.span()  # 返回每个匹配坐标
                obj.setStatus(label)
                ner_label = label
                # if ner_label in ['JF', 'YF', 'LH']:
                #     ner_label = 'ORG'
                tag_arr[begin] = 'B-' + ner_label
                for index in range(begin + 1, end):
                    tag_arr[index] = 'I-' + ner_label
                isMask = True

    return isMask


def finditer(cws_cut_cent, val):
    iters = []
    begin = end = -1
    for i in range(len(cws_cut_cent)):
        cws = cws_cut_cent[i]
        if val.startswith(cws):
            begin = i
        if val.endswith(cws):
            end = i + 1
        if begin != -1 and end > begin:
            tmp = ''.join(cws_cut_cent[begin:end])
            if tmp == val:
                iters.append((begin, end))
                begin = end = -1

    return iters


def mask_contract_field_word(context, cws_cut_cent, val, tag_arr, label, obj, isnum):
    isMask = False
    if val != 'fddcUndefined':
        if context.find(val) != -1:
            iters = finditer(cws_cut_cent, val)
            for begin, end in iters:
                obj.setStatus(label)
                ner_label = label
                tag_arr[begin] = 'B-' + ner_label
                for index in range(begin + 1, end):
                    tag_arr[index] = 'I-' + ner_label
                isMask = True

    return isMask


maketrain_word()

# maketrain_word_debug('1380579')

# maketrain_char(before=0)
# showText()
# discoverText(before=0)
