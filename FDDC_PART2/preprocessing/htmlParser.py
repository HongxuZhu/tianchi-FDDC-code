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
def levelText_withtable(htmlpath):
    soup = BeautifulSoup(open(htmlpath), 'lxml')
    s_arr = []
    for paragraph in soup.find_all('div', type='paragraph'):
        p_title = paragraph.attrs.get('title')
        if p_title is not None:
            p_title = normalizer.norm(p_title)
            if len(p_title) > 0:
                s_arr.append(p_title)
        for content in paragraph.find_all('div', type='content'):
            c_title = content.attrs.get('title')
            if c_title is not None:
                c_title = normalizer.norm(c_title)
                if len(c_title) > 0:
                    s_arr.append(c_title)
            tables = content.find_all('table')
            # 假设训练数据中，text和table不同时存在于同一content内
            if len(tables) == 0:
                sentences = content.get_text().split('。')
                for sentence in sentences:
                    # 合并，英语怎么处理？
                    sen = normalizer.norm(sentence)
                    if len(sen) > 0:
                        s_arr.append(sen)
                        # print(sen)
            else:
                for table in tables:
                    t_title = table.attrs.get('title')
                    if t_title is not None:
                        t_title = normalizer.norm(t_title)
                        if len(t_title) > 0:
                            s_arr.append(t_title)
                    for tr in table.find_all('tr'):
                        td_arr = []
                        for td in tr.find_all('td'):
                            td_text = normalizer.norm(td.get_text())
                            if len(td_text) > 0:
                                td_arr.append(td_text)
                        if len(td_arr) > 0:
                            s_arr.append('╫'.join(td_arr))
                            # print(td_arr)
    return s_arr

# testlpath + '1153.html'
# /home/utopia/corpus/FDDC_part2_data/round1_train_20180518/增减持/html/10243.html
# print(levelText(testlpath + '1153.html'))
# print(levelText_withtable('/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/重大合同/html/16773644.html'))
