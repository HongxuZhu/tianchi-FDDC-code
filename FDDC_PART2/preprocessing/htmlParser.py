from bs4 import BeautifulSoup
import pandas as pd
import FDDC_PART2.utils.dataframe as dfutil

htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/html/'


# soup = BeautifulSoup(open(htmlpath + '7880.html'), 'html5lib')
# for table in soup.find_all('table'):
# print(table.get_text())
# print(table.find_parent().get_text())
# print(table.prettify())
def call(cell):
    print(cell)


def show_header(htmlpath, val):
    with open(htmlpath, 'r') as f:
        dfs = pd.read_html(f.read(), flavor='html5lib')
        # dfs = pd.read_html(f.read(), match=val, flavor='html5lib')
        for df in dfs:
            # print(dfutil.firstcol(df))  # 第一列
            print(dfutil.firstrow(df))  # 第一行
            print('-------------------------------')
            # dfutil.locate(df, val)
