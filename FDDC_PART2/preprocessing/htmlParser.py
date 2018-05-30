from bs4 import BeautifulSoup
import pandas as pd

htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/html/'

# soup = BeautifulSoup(open(htmlpath + '7880.html'), 'html5lib')
# for table in soup.find_all('table'):
# print(table.get_text())
# print(table.find_parent().get_text())
# print(table.prettify())

with open(htmlpath + '7880.html', 'r') as f:
    dfs = pd.read_html(f.read(), flavor='html5lib')
    for df in dfs:
        print(df)
        print('-----------------------------------------------------------')
