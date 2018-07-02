import re
import random
from decimal import Decimal
from bs4 import BeautifulSoup

from FDDC_PART2.preprocessing.QANetTrainFile import getDingZengUnion
from FDDC_PART2_V1.nlp.tokenize.cws import jieba_tokenize
from FDDC_PART2_V1.preprocess.tableHandler import table2array

random.seed(1987)
# 公告id,增发对象,发行方式,增发数量,增发金额,锁定期,认购方式
dz_trainpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/dingzeng.train'
dz_htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/html/'

reg_duixiang = '(' \
               '(关联|担保|发行|法定代表|获配|配售|认购|申购|投资|询价|报价|合伙|交易)' \
               '(对象|对方|方|人|者|机构|主体)' \
               '|股东)' \
               '(名称|全称|姓名|名册)?'  # $
pattern_duixiang = re.compile(reg_duixiang)


def searchTable3(sample=1, enhance=1):
    dz_train = open('dz_att_cls_table.train', 'a+')
    dz_dev = open('dz_att_cls_table.dev', 'a+')

    dingzengs = getDingZengUnion(dz_trainpath)
    for id in dingzengs.keys():
        dzs = dingzengs[id]
        htmlpath = dz_htmlpath + id + '.html'

        rank = 6
        mod = int(id) % rank
        if mod == 0:
            makefile = dz_dev
        else:
            makefile = dz_train

        soup = BeautifulSoup(open(htmlpath), 'lxml')
        tables = soup.find_all('table')
        for table in tables:  # 遍历所有table
            cuts = table2array(table)  # 将table转为二维数组
            for cut in cuts:  # 遍历规整行列数组
                rows = len(cut)
                cols = len(cut[0])
                for row in range(rows):
                    for col in range(cols):

                        valuecell = cut[row][col]
                        topcell = cut[0][col]
                        leftcell = cut[row][0]

                        # if matchDuixiang(topcell) or matchDuixiang(leftcell):
                        labels = set()
                        # for dz in dzs:
                        #     if hasAtt(valuecell, dz.duixiang, 'DX', dz, False, None, None):
                        #         labels.add('__label__dzdx')
                        #     if hasAtt(valuecell, dz.shuliang, 'SL', dz, True, topcell, leftcell):
                        #         labels.add('__label__dzsl')
                        #     if hasAtt(valuecell, dz.jine, 'JE', dz, True, topcell, leftcell):
                        #         labels.add('__label__dzje')

                        for dz in dzs:
                            if hasAtt(valuecell, dz.duixiang, 'DX', dz, False, None, None, False) \
                                    and not hasAtt(topcell + leftcell, dz.duixiang, 'DX', dz, False, None, None, False):
                                labels.add('__label__dzdx')
                            if hasAtt(valuecell, dz.shuliang, 'SL', dz, True, topcell, leftcell, False) \
                                    and not hasAtt(topcell + leftcell, dz.shuliang, 'SL', dz, True, topcell, leftcell, False):
                                labels.add('__label__dzsl')
                            if hasAtt(valuecell, dz.jine, 'JE', dz, True, topcell, leftcell, False) \
                                    and not hasAtt(topcell + leftcell, dz.shuliang, 'SL', dz, True, topcell, leftcell, False):
                                labels.add('__label__dzje')

                        if len(labels) == 0:
                            labels.add('__label__nothing')

                        if row == 0 and col == 0:
                            pass
                        elif row == 0 and col != 0:
                            valuecell = leftcell + valuecell
                        elif row != 0 and col == 0:
                            valuecell = topcell + valuecell
                        else:
                            valuecell = topcell + leftcell + valuecell

                        toline = ' '.join(labels) + ' ' + ' '.join(jieba_tokenize(valuecell)) + '\n'
                        makefile.write(toline)

        for dz in dzs:
            dz.desc()


def hasAtt(line_source, val, label, dingzeng, isNum, top, left, strict):
    if val != 'fddcUndefined':
        val = val.replace('(', '\(')
        val = val.replace(')', '\)')
        val = val.replace('[', '\[')
        val = val.replace(']', '\]')
        if isNum:
            if top.find('万') != -1 or left.find('万') != -1:
                val = str((Decimal(val) / 10000))
        if strict:
            if val == line_source:  # 完全匹配
                dingzeng.setStatus(label)
                return True
        else:
            if re.search(val, line_source, re.I) is not None:  # 部分匹配
                dingzeng.setStatus(label)
                return True

    return False


def matchDuixiang(cell):
    if pattern_duixiang.search(cell) is not None:
        return True
    return False

# catTable()
# searchTable3(sample=1, enhance=1)
