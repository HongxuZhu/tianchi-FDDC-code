import re

from bs4 import BeautifulSoup

from FDDC_PART2.preprocessing.QANetTrainFile import getDingZengUnion
from FDDC_PART2_V1.nlp.classification.textCls import getModel, predict
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

dataroot = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/nlp/NER_IDCNN_CRF/data/'
model_path = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/nlp/classification/cooking.ftz'
dz_pk_cls_table_model = getModel(model_path)


def searchTable3():
    dz_train = open(dataroot + 'dz_pk_table.train', 'a+')
    dz_dev = open(dataroot + 'dz_pk_table.dev', 'a+')

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
                        tag_arr = ['O'] * len(valuecell)
                        top_arr = ['O'] * len(topcell)
                        left_arr = ['O'] * len(leftcell)

                        isTrain = False
                        for dz in dzs:
                            if mask_contract_field(valuecell, dz.duixiang, tag_arr, 'DX', dz):
                                isTrain = True

                        if isTrain:

                            if row == 0 and col == 0:
                                pass
                            elif row == 0 and col != 0:
                                valuecell = leftcell + valuecell
                                tag_arr = left_arr + tag_arr
                            elif row != 0 and col == 0:
                                valuecell = topcell + valuecell
                                tag_arr = top_arr + tag_arr
                            else:
                                valuecell = topcell + leftcell + valuecell
                                tag_arr = top_arr + left_arr + tag_arr

                            for i in range(len(valuecell)):
                                makefile.write(valuecell[i] + ' ' + tag_arr[i] + '\n')
                            makefile.write('\n')

        for dz in dzs:
            dz.desc()


def mask_contract_field(line_source, val, tag_arr, label, dingzeng):
    isMask = False
    if val != 'fddcUndefined':
        val = val.replace('(', '\(')
        val = val.replace(')', '\)')
        val = val.replace('[', '\[')
        val = val.replace(']', '\]')
        iters = re.finditer(val, line_source, re.I)
        for iter in iters:
            begin, end = iter.span()  # 返回每个匹配坐标
            dingzeng.setStatus(label)
            tag_arr[begin] = 'B-' + label
            for index in range(begin + 1, end):
                tag_arr[index] = 'I-' + label
            isMask = True
    return isMask


def matchDuixiang(cell):
    label = predict(dz_pk_cls_table_model, cell)
    if label == '__label__dzpk':
        # if pattern_duixiang.search(cell) is not None:
        return True
    return False


# catTable()
searchTable3()
