import re

import pandas as pd
from bs4 import BeautifulSoup

import FDDC_PART2.preprocessing.normalizer as normalizer
import FDDC_PART2.utils.dataframe as dfutil

testlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/重大合同/html/'


def call(cell):
    print(cell)


def show_header(htmlpath, val):
    try:
        with open(htmlpath, 'r') as f:
            dfs = pd.read_html(f.read(), match=val, flavor='lxml')  # html5lib 有bug
            for df in dfs:
                # print(dfutil.firstcol(df))  # 第一列
                # print(dfutil.firstrow(df))  # 第一行
                head = dfutil.locate(df, val)
                return head
    except:
        pass


# bug 未修复：句子比实际多
def levelText(htmlpath):
    soup = BeautifulSoup(open(htmlpath), 'lxml')
    tag = soup.table
    if tag is not None:
        tag.clear()  # 此时table文法是噪音
    s_arr = []
    for paragraph in soup.find_all('div', type='paragraph'):
        for content in paragraph.find_all('div', type='content'):
            sentences = content.get_text().split('。')
            for sentence in sentences:
                sen = re.sub('\s+', '', sentence)  # 合并，英语怎么处理？
                sen = normalizer.norm_number(sen)
                if len(sen) > 0:
                    s_arr.append(sen)
    return s_arr


def levelText_withtable(htmlpath):
    soup = BeautifulSoup(open(htmlpath), 'lxml')
    s_arr = []
    for paragraph in soup.find_all('div', type='paragraph'):
        for content in paragraph.find_all('div', type='content'):
            tables = content.find_all('table')
            if len(tables) == 0:  # 假设训练数据中，text和table不同时存在
                sentences = content.get_text().split('。')
                for sentence in sentences:
                    sen = re.sub('\s+', '', sentence)  # 合并，英语怎么处理？
                    sen = normalizer.norm_number(sen)
                    if len(sen) > 0:
                        s_arr.append(sen)
                        # print(sen)
            else:
                for table in tables:
                    for tr in table.find_all('tr'):
                        td_arr = []
                        for td in tr.find_all('td'):
                            td_text = re.sub('\s+', '', td.get_text())
                            if len(td_text) > 0:
                                td_arr.append(td_text)
                        if len(td_arr) > 0:
                            s_arr.append('～'.join(td_arr))
                            # print(td_arr)
    return s_arr

# testlpath + '1153.html'
# /home/utopia/corpus/FDDC_part2_data/round1_train_20180518/增减持/html/10243.html
# print(levelText(testlpath + '1153.html'))

# print(levelText_withtable('/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/html/12088.html'))
