import os
from pyltp import Segmentor

import html2text

from FDDC_PART2.preprocessing.htmlParser import levelText_withglove

dz_train_htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/html/'
ht_train_htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/重大合同/html/'
zjc_train_htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/增减持/html/'

dz_test_htmlpath = '/home/utopia/corpus/FDDC_part2_data/FDDC_announcements_round1_test_a_20180605/定增/html/'
ht_test_htmlpath = '/home/utopia/corpus/FDDC_part2_data/FDDC_announcements_round1_test_a_20180605/重大合同/html/'
zjc_test_htmlpath = '/home/utopia/corpus/FDDC_part2_data/FDDC_announcements_round1_test_a_20180605/增减持/html/'

linelimit = 100000

h2t = html2text.HTML2Text()
h2t.ignore_links = True
h2t.ignore_images = True
h2t.ignore_emphasis = True

cws_model_path = '/home/utopia/corpus/ltp_data_v3.4.0/cws.model'  # ltp模型目录的路径
segmentor = Segmentor()  # 初始化实例
segmentor.load(cws_model_path)  # 加载模型


def sss(rootdir, cutmethod, fddcfile):
    list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(list)):
        htmlpath = os.path.join(rootdir, list[i])
        if os.path.isfile(htmlpath):
            s_arr = levelText_withglove(htmlpath)
            if len(s_arr) > 0:
                for sentence in s_arr:
                    fddcfile.write(' ' + ' '.join(cutmethod(sentence)))
                fddcfile.flush()
            print(htmlpath)


def cut_word(sentence):
    words = segmentor.segment(sentence)  # 分词
    words_list = list(words)
    return words_list


def cut_char(sentence):
    words_list = []
    for c in sentence:
        words_list.append(c)
    return words_list


def glovefile():
    fddcfile = open('/home/utopia/github/glove/fddc_part2_char.text', 'a+')
    sss(dz_train_htmlpath, cut_char, fddcfile)
    sss(ht_train_htmlpath, cut_char, fddcfile)
    sss(zjc_train_htmlpath, cut_char, fddcfile)
    sss(dz_test_htmlpath, cut_char, fddcfile)
    sss(ht_test_htmlpath, cut_char, fddcfile)
    sss(zjc_test_htmlpath, cut_char, fddcfile)
    segmentor.release()


glovefile()
