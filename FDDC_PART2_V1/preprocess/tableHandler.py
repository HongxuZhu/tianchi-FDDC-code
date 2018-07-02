import re

from bs4 import BeautifulSoup

from FDDC_PART2.preprocessing.QANetTrainFile import getDingZengUnion
from FDDC_PART2.preprocessing.normalizer import norm_dz


def table2array(table):
    rowspan_dict = {}
    trs = list(table.find_all('tr'))
    tr_list = []
    for trnum in range(len(trs)):
        td_list = []
        tds = list(trs[trnum].find_all('td'))
        for tdnum in range(len(tds)):
            # td.rowspan
            cell = tds[tdnum]
            rowspan = cell.attrs.get('rowspan')
            colspan = cell.attrs.get('colspan')
            if rowspan is not None:
                rowspan_dict[(trnum, tdnum)] = int(rowspan)

            text = norm_dz(cell.get_text())
            if colspan is not None:
                for it in range(int(colspan)):
                    # 只影响本行
                    td_list.append(text)  # 此处是否妥当?
            else:
                td_list.append(text)
        tr_list.append(td_list)

    if len(rowspan_dict) > 0:
        keys = list(rowspan_dict.keys())
        keys.sort(key=lambda x: (x[1], x[0]))  # 从左上至右下排序
        for key in keys:
            span = rowspan_dict[key]
            row = key[0]
            col = key[1]
            for i in range(row + 1, row + span):
                # 影响下面若干行
                tr_list[i] = tr_list[i][0:col] + [''] + tr_list[i][col:]

    return cutTable(tr_list)


def cutTable(t2a):
    cut = []
    if len(t2a) > 0:
        current_colnum = len(t2a[0])
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
