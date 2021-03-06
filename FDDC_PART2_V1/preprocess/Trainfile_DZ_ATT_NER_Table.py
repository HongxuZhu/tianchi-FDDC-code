import os
import re
from decimal import Decimal

from bs4 import BeautifulSoup

from FDDC_PART2.preprocessing.QANetTrainFile import getDingZengUnion
from FDDC_PART2_V1.nlp.classification.textCls import getModel, predict
from FDDC_PART2_V1.preprocess.Trainfile_DZ_ATT_CLS_Table import hasAtt
from FDDC_PART2_V1.preprocess.tableHandler import table2array
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
                    density = float(effective / (5 * len(dz_tmp_list)))  # 有效数据密度
                    if density > 0.2:
                        dz_tmp_list_dict[(t1, t2)] = (dx_weight, effective, dz_tmp_list, tag)

        # paixu = list(sorted(dz_tmp_list_dict.items(), key=lambda d: d[1][0], reverse=True))
        # 按对象表头权重×密度倒排
        paixu = list(sorted(dz_tmp_list_dict.items(), key=lambda d: d[1][0] * float(d[1][1] / (5 * len(d[1][2]))), reverse=True))

        if len(dzs) != 1 and (len(paixu) == 0 or len(dzs) != len(paixu[0][1][2])):
            for dz in dzs:
                print('HTMLID= {} |DX= {} |数量= {} |金额= {} |锁定= {} |认购= {} '
                      .format(dz.id, dz.duixiang, dz.shuliang, dz.jine, dz.suoding, dz.rengou))
            print(
                '以上结果为真实------------------------------------------------------------------------------------------------')
            if len(paixu) > 0:
                p = paixu[0]
                key = p[0]
                val = p[1]
                dx_weight = val[0]
                effective = val[1]
                dz_tmp_list = val[2]
                tag = val[3]
                for tmp in dz_tmp_list:
                    tmp.desc()
                print('tag=( {} ),dx_weight=( {} ),effective=( {} )'.format(tag, dx_weight, str(effective)))
            print(
                '以上结果为预测------------------------------------------------------------------------------------------------')
            print('\n')


def debug(id, rootdir):
    htmlpath = os.path.join(rootdir, id)
    id = id.replace('.html', '')
    if os.path.isfile(htmlpath):
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
                    density = float(effective / (5 * len(dz_tmp_list)))  # 有效数据密度
                    if density > 0.2:
                        dz_tmp_list_dict[(t1, t2)] = (dx_weight, effective, dz_tmp_list, tag, density)

        # paixu = list(sorted(dz_tmp_list_dict.items(), key=lambda d: d[1][0], reverse=True))
        paixu = list(sorted(dz_tmp_list_dict.items(), key=lambda d: d[1][0] * d[1][4], reverse=True))

        for p in paixu:
            key = p[0]
            val = p[1]
            effective = val[1]
            dz_tmp_list = val[2]
            tag = val[3]
            density = val[4]
            for tmp in dz_tmp_list:
                tmp.desc()
            print('tag=( {} ),effective=( {} ),density=( {} )'.format(tag, str(effective), str(density)))
            print('以上结果为预测------------------------------------------------------------------------------------------------')
        print('\n')


def writeTable():
    submit_path_ht = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/submit_sample/dingzeng.text'
    # submit_path_ht = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/submit_sample/train/dingzeng.test'
    submit_path_file = open(submit_path_ht, 'a+')
    submit_path_file.write('公告id\t增发对象\t增发数量\t增发金额\t锁定期\t认购方式\n')
    rootdir = '/home/utopia/corpus/FDDC_part2_data/FDDC_announcements_round1_test_b_20180708/定增/html/'
    # rootdir = dz_htmlpath
    filelist = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(filelist)):
        id = filelist[i]
        htmlpath = os.path.join(rootdir, id)
        id = id.replace('.html', '')
        if os.path.isfile(htmlpath):
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
                        density = float(effective / (5 * len(dz_tmp_list)))  # 有效数据密度
                        if density > 0.2:
                            dz_tmp_list_dict[(t1, t2)] = (dx_weight, effective, dz_tmp_list, tag, density)

            # paixu = list(sorted(dz_tmp_list_dict.items(), key=lambda d: d[1][0], reverse=True))
            paixu = list(sorted(dz_tmp_list_dict.items(), key=lambda d: d[1][0] * d[1][4], reverse=True))

            if len(paixu) > 0:
                p = paixu[0]
                key = p[0]
                val = p[1]
                effective = val[1]
                dz_tmp_list = val[2]
                tag = val[3]
                density = val[4]
                for tmp in dz_tmp_list:
                    tmp.desc()
                    submit_dz(tmp, submit_path_file)
                print('tag=( {} ),effective=( {} ),density=( {} )'.format(tag, str(effective), str(density)))
            print(
                '以上结果为预测------------------------------------------------------------------------------------------------')
            print('\n')


def submit_dz(tmp, submit_path_file):
    dz = []
    dz.append(tmp.id)
    dz.append(tmp.duixiang)
    dz.append(tmp.shuliang if tmp.shuliang != 'fddcUndefined' else '')
    dz.append(tmp.jine if tmp.jine != 'fddcUndefined' else '')
    dz.append(tmp.suoding if tmp.suoding != 'fddcUndefined' else '12')
    dz.append('现金' if tmp.rengou != 'fddcUndefined' else '现金')

    line = '\t'.join(dz) + '\n'
    submit_path_file.write(line)


# 用于调试表格策略
# showTable()

# 用于生成提交数据
writeTable()
# debug('15524495.html', dz_htmlpath)

# 用于发现表头规律
# searchTable3()
