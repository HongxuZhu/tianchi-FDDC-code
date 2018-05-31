from bs4 import BeautifulSoup
import pandas as pd
import FDDC_PART2.utils.dataframe as dfutil
import re

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
                sen = re.sub('\s+', '', sentence)  # 合并
                if len(sen) > 0:
                    s_arr.append(sen)
    return s_arr

# testlpath + '1153.html'
# /home/utopia/corpus/FDDC_part2_data/round1_train_20180518/增减持/html/10243.html
# print(levelText(testlpath + '1153.html'))
