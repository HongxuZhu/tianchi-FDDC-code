import re

from bs4 import BeautifulSoup

from FDDC_PART2.preprocessing.QANetTrainFile import getDingZengUnion
from FDDC_PART2_V1.nlp.tokenize.cws import ltp_tokenize
from FDDC_PART2_V1.preprocess.tableHandler import table2array

# 公告id,增发对象,发行方式,增发数量,增发金额,锁定期,认购方式
dz_trainpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/dingzeng.train'
dz_htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/html/'

reg_duixiang = '(' \
               '(关联|担保|发行|法定代表|获配|配售|认购|申购|投资|询价|报价|合伙|交易)' \
               '(对象|对方|方|人|者|机构|主体)' \
               '|股东)' \
               '(名称|全称|姓名|名册)?'  # $
pattern_duixiang = re.compile(reg_duixiang)


def searchTable3():
    dz_train = open('dz_pk_cls.train', 'a+')
    dz_dev = open('dz_pk_cls.dev', 'a+')

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

                        if row == 0 and col == 0:
                            # if matchDuixiang(valuecell):
                            label = '__label__nothing '
                            for dz in dzs:
                                if hasPK(valuecell, dz.duixiang, 'DX', dz):
                                    label = '__label__dzpk '
                                    break
                            toline = label + ' '.join(ltp_tokenize(valuecell)) + '\n'
                            makefile.write(toline)
                        elif row == 0 and col != 0:
                            # if matchDuixiang(leftcell):
                            label = '__label__nothing '
                            for dz in dzs:
                                if hasPK(valuecell, dz.duixiang, 'DX', dz):
                                    label = '__label__dzpk '
                                    break

                            valuecell = leftcell + valuecell
                            toline = label + ' '.join(ltp_tokenize(valuecell)) + '\n'
                            makefile.write(toline)
                        elif row != 0 and col == 0:
                            # if matchDuixiang(topcell):
                            label = '__label__nothing '
                            for dz in dzs:
                                if hasPK(valuecell, dz.duixiang, 'DX', dz):
                                    label = '__label__dzpk '
                                    break

                            valuecell = topcell + valuecell
                            toline = label + ' '.join(ltp_tokenize(valuecell)) + '\n'
                            makefile.write(toline)
                        else:
                            # if matchDuixiang(topcell) or matchDuixiang(leftcell):  # 定位到对象列
                            label = '__label__nothing '
                            for dz in dzs:
                                if hasPK(valuecell, dz.duixiang, 'DX', dz):
                                    label = '__label__dzpk '
                                    break

                            valuecell = topcell + leftcell + valuecell
                            toline = label + ' '.join(ltp_tokenize(valuecell)) + '\n'
                            makefile.write(toline)

        for dz in dzs:
            dz.desc()


def hasPK(line_source, val, label, dingzeng):
    if val != 'fddcUndefined':
        val = val.replace('(', '\(')
        val = val.replace(')', '\)')
        val = val.replace('[', '\[')
        val = val.replace(']', '\]')
        if re.search(val, line_source, re.I) is not None:
            dingzeng.setStatus(label)
            return True
    return False


def matchDuixiang(cell):
    if pattern_duixiang.search(cell) is not None:
        return True
    return False


# catTable()
searchTable3()
