import re

from bs4 import BeautifulSoup

from FDDC_PART2.preprocessing.QANetTrainFile import getDingZengUnion

# 公告id,增发对象,发行方式,增发数量,增发金额,锁定期,认购方式
dz_trainpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/dingzeng.train'
dz_htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/html/'

reg_duixiang = '(' \
               '(关联|担保|发行|法定代表|获配|配售|认购|申购|投资|询价|报价|合伙|交易)' \
               '(对象|对方|方|人|者|机构|主体)' \
               '|股东)' \
               '(名称|全称|姓名|名册)?'
pattern_duixiang = re.compile(reg_duixiang)

dataroot = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2/expand/NER_IDCNN_CRF/data/'

dz_train = open(dataroot + 'dz.train', 'a+')
dz_dev = open(dataroot + 'dz.dev', 'a+')


def catTable():
    trigger_dict = {}
    dingzengs = getDingZengUnion(dz_trainpath)
    for id in dingzengs.keys():
        dzs = dingzengs[id]
        htmlpath = dz_htmlpath + id + '.html'
        soup = BeautifulSoup(open(htmlpath), 'lxml')
        tables = soup.find_all('table')
        for table in tables:
            t2a = table2array(table)
            if len(t2a) > 0:
                cuts = cutTable(t2a)
                for cut in cuts:
                    for dz in dzs:
                        val = dz.duixiang
                        if val != 'fddcUndefined':
                            triggers = locateAll(cut, val)
                            if len(triggers) > 0:
                                for trigger in triggers:
                                    top = trigger[0]
                                    left = trigger[1]

                                    if len(top) > 1 and len(top) < 8:
                                        if trigger_dict.get(top):
                                            trigger_dict[top] += 1
                                        else:
                                            trigger_dict[top] = 1

                                    if len(left) > 1 and len(left) < 8:
                                        if trigger_dict.get(left):
                                            trigger_dict[left] += 1
                                        else:
                                            trigger_dict[left] = 1

    guolv = {k: v for k, v in trigger_dict.items() if v > 9}
    paixu = sorted(guolv.items(), key=lambda d: d[1], reverse=True)
    print(paixu)
    print('---------------------------------------------------------')
    for px in paixu:
        print(px[0] + '\t' + str(px[1]))


def table2array(table):
    trs = table.find_all('tr')
    tr_list = []
    for tr in trs:
        td_list = []
        tds = tr.find_all('td')
        for td in tds:
            cell = re.sub('\s+', '', td.get_text())
            td_list.append(cell)
        tr_list.append(td_list)
    return tr_list


def cutTable(t2a):
    current_colnum = len(t2a[0])
    cut = []
    tmp = []
    for r in range(len(t2a)):
        tr = t2a[r]
        this_colnum = len(tr)
        if this_colnum == current_colnum:
            tmp.append(tr)
        else:
            cut.append(tmp)
            tmp = []
            tmp.append(tr)
            current_colnum = this_colnum
        if r == (len(t2a) - 1):
            cut.append(tmp)
    return cut


def locateAll(t2a, val):
    rownum = len(t2a)
    colnum = len(t2a[0])
    triggers = []
    for r in range(rownum):
        for c in range(colnum):
            cell = t2a[r][c]
            if cell == val:
                top = t2a[0][c]
                left = t2a[r][0]
                triggers.append((top, left))
    return triggers


def searchTable():
    dingzengs = getDingZengUnion(dz_trainpath)
    for id in dingzengs.keys():
        dzs = dingzengs[id]
        htmlpath = dz_htmlpath + id + '.html'
        print(htmlpath)

        rank = 6
        mod = int(id) % rank
        if mod == 0:
            makefile = dz_dev
        else:
            makefile = dz_train

        soup = BeautifulSoup(open(htmlpath), 'lxml')
        tables = soup.find_all('table')
        for table in tables:  # 遍历所有table
            t2a = table2array(table)  # 将table转为二维数组
            if len(t2a) > 0:
                cuts = cutTable(t2a)  # 将二维数组切割为规整行列
                for cut in cuts:  # 遍历规整行列数组
                    head = cut[0]
                    cols = len(head)
                    rows = len(cut)
                    if rows > 1:
                        for col in range(cols):
                            headcell = head[col]
                            if matchDuixiang(headcell):  # 定位到对象列
                                # 遍历该列下所有对应cell
                                for row in range(0, rows):
                                    cell = cut[row][col] + '|'
                                    tag_arr = ['O'] * len(cell)
                                    for dz in dzs:
                                        val = dz.duixiang
                                        mask_contract_field(cell, val, tag_arr, 'DX', dz)
                                    for i in range(len(cell)):
                                        makefile.write(cell[i] + ' ' + tag_arr[i] + '\n')
                                    makefile.write('\n')


def mask_contract_field(line_source, val, tag_arr, label, dingzeng):
    if val != 'fddcUndefined':
        val = val.replace('(', '\(')
        val = val.replace(')', '\)')
        val = val.replace('[', '\[')
        val = val.replace(']', '\]')
        iters = re.finditer(val, line_source, re.I)
        for iter in iters:
            begin, end = iter.span()  # 返回每个匹配坐标
            # contract.setStatus(label)
            tag_arr[begin] = 'B-' + label
            for index in range(begin + 1, end):
                tag_arr[index] = 'I-' + label


def matchDuixiang(cell):
    if pattern_duixiang.search(cell) is not None:
        return True
    return False


# catTable()
searchTable()
# print(matchDuixiang('交易w对方'))
