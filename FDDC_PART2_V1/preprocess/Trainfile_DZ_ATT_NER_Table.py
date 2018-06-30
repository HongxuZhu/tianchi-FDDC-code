import re
from decimal import Decimal
from bs4 import BeautifulSoup

from FDDC_PART2.preprocessing.QANetTrainFile import getDingZengUnion
from FDDC_PART2_V1.nlp.classification.textCls import getModel, predict
from FDDC_PART2_V1.preprocess.tableHandler import table2array
from FDDC_PART2_V1.preprocess.Trainfile_DZ_ATT_CLS_Table import hasAtt
from FDDC_PART2_V1.rules.dingzengPackage import table_tag_byrow

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
model_path = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/nlp/classification/dz_pk_cls_table.ftz'
dz_pk_cls_table_model = getModel(model_path)

submit_path_ht = 'submit_sample/hetong.csv'
submit_path_file = open(submit_path_ht, 'a+', encoding='gbk')
submit_path_file.write('公告id,甲方,乙方,项目名称,合同名称,合同金额上限,合同金额下限,联合体成员\n')

def searchTable3():
    dz_train = open(dataroot + 'dz_att_table.train', 'a+')
    dz_dev = open(dataroot + 'dz_att_table.dev', 'a+')

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
                        topcell = cut[0][col] + '|'
                        leftcell = cut[row][0] + '|'
                        tag_arr = ['O'] * len(valuecell)
                        top_arr = ['O'] * len(topcell)
                        left_arr = ['O'] * len(leftcell)

                        isTrain = False
                        for dz in dzs:
                            if mask_contract_field(valuecell, dz.duixiang, tag_arr, 'DX', dz, False, None, None):
                                isTrain = True
                            if mask_contract_field(valuecell, dz.shuliang, tag_arr, 'SL', dz, True, topcell, leftcell):
                                isTrain = True
                            if mask_contract_field(valuecell, dz.jine, tag_arr, 'JE', dz, True, topcell, leftcell):
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


def mask_contract_field(line_source, val, tag_arr, label, dingzeng, isNum, top, left):
    isMask = False
    if val != 'fddcUndefined':
        val = val.replace('(', '\(')
        val = val.replace(')', '\)')
        val = val.replace('[', '\[')
        val = val.replace(']', '\]')
        if isNum:
            if top.find('万') != -1 or left.find('万') != -1:
                val = str((Decimal(val) / 10000))
                iters = re.finditer(val, line_source, re.I)
                for iter in iters:
                    begin, end = iter.span()  # 返回每个匹配坐标
                    dingzeng.setStatus(label)
                    tag_arr[begin] = 'B-' + label + '_unit10k'
                    for index in range(begin + 1, end):
                        tag_arr[index] = 'I-' + label + '_unit10k'
                    isMask = True
            else:
                iters = re.finditer(val, line_source, re.I)
                for iter in iters:
                    begin, end = iter.span()  # 返回每个匹配坐标
                    dingzeng.setStatus(label)
                    tag_arr[begin] = 'B-' + label + '_unit1'
                    for index in range(begin + 1, end):
                        tag_arr[index] = 'I-' + label + '_unit1'
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


def matchDuixiang(cell):
    label = predict(dz_pk_cls_table_model, cell)
    if label == '__label__dzpk':
        # if pattern_duixiang.search(cell) is not None:
        return True
    return False


def catTable():
    trigger_dict = {}
    dingzengs = getDingZengUnion(dz_trainpath)
    for id in dingzengs.keys():
        dzs = dingzengs[id]
        htmlpath = dz_htmlpath + id + '.html'
        soup = BeautifulSoup(open(htmlpath), 'lxml')
        tables = soup.find_all('table')
        for table in tables:
            cuts = table2array(table)
            for cut in cuts:  # 遍历规整行列数组
                rows = len(cut)
                cols = len(cut[0])
                for row in range(rows):
                    for col in range(cols):
                        valuecell = cut[row][col]
                        topcell = cut[0][col]
                        leftcell = cut[row][0]
                        for dz in dzs:
                            if hasAtt(valuecell, dz.duixiang, 'DX', dz, False, None, None, False):
                                # if hasAtt(valuecell, dz.shuliang, 'SL', dz, True, topcell, leftcell, False):
                                # if hasAtt(valuecell, dz.jine, 'JE', dz, True, topcell, leftcell, False):
                                # if hasAtt(valuecell, dz.suoding, 'SD', dz, False, topcell, leftcell, True):
                                # if hasAtt(valuecell, dz.rengou, 'RG', dz, False, topcell, leftcell, True):
                                if len(topcell) > 1 and len(topcell) < 8:
                                    if trigger_dict.get(topcell):
                                        trigger_dict[topcell] += 1
                                    else:
                                        trigger_dict[topcell] = 1
                                if len(leftcell) > 1 and len(leftcell) < 8:
                                    if trigger_dict.get(leftcell):
                                        trigger_dict[leftcell] += 1
                                    else:
                                        trigger_dict[leftcell] = 1

    guolv = {k: v for k, v in trigger_dict.items() if v > 9}
    paixu = sorted(guolv.items(), key=lambda d: d[1], reverse=True)
    print('--------------------------------------------------------------------------------------------------------')
    for px in paixu:
        print(px[0] + '\t' + str(px[1]))


def showTable():
    dingzengs = getDingZengUnion(dz_trainpath)
    for id in dingzengs.keys():
        dzs = dingzengs[id]
        htmlpath = dz_htmlpath + id + '.html'
        soup = BeautifulSoup(open(htmlpath), 'lxml')
        tables = list(soup.find_all('table'))
        dz_tmp_list_dict = {}
        for t1 in range(len(tables)):
            table = tables[t1]
            cuts = table2array(table)
            for t2 in range(len(cuts)):
                cut = cuts[t2]
                dx_weight, effective, dz_tmp_list, tag = table_tag_byrow(id, cut)
                if dx_weight > 0 and effective > 0:
                    dz_tmp_list_dict[(t1, t2)] = (dx_weight, effective, dz_tmp_list, tag)

        paixu = list(sorted(dz_tmp_list_dict.items(), key=lambda d: d[1][0], reverse=True))

        if len(dzs) != 1 and (len(paixu) == 0 or len(dzs) != len(paixu[0][1][2])):
            for dz in dzs:
                print('HTMLID= {} |对象= {} |数量= {} |金额= {} |锁定= {} |认购= {} '
                      .format(dz.id, dz.duixiang, dz.shuliang, dz.jine, dz.suoding, dz.rengou))
            print(
                '以上结果为真实------------------------------------------------------------------------------------------------')
            if len(paixu) > 0:
                p = paixu[0]
                key = p[0]
                val = p[1]
                effective = val[1]
                dz_tmp_list = val[2]
                tag = val[3]
                for tmp in dz_tmp_list:
                    tmp.desc()
                print('tag=( {} ),effective=( {} )'.format(tag, str(effective)))
            print(
                '以上结果为预测------------------------------------------------------------------------------------------------')
            print('\n')


def submit_dz(ht, submit_path_file):
    pid = ht[0]
    near_jf = ht[1]
    yfword = ht[2]
    near_xm = ht[3]
    near_ht = ht[4]
    near_au = ht[5]
    near_ad = ht[6]
    near_lh = ht[7]
    print('pid={},JF={},YF={},XM={},HT={},AU={},AD={},LH={}'
          .format(pid, near_jf, yfword, near_xm, near_ht, near_au, near_ad, near_lh))

    line = ','.join(ht) + '\n'
    submit_path_file.write(line)


showTable()
# searchTable3()
