import FDDC_PART2.preprocessing.htmlParser as paser
import re

# 公告id,增发对象,发行方式,增发数量,增发金额,锁定期,认购方式
dz_trainpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/dingzeng.train'
dz_htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/html/'

# 公告id,甲方,乙方,项目名称,合同名称,合同金额上限,合同金额下限,联合体成员
ht_trainpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/重大合同/hetong.train'
ht_htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/重大合同/html/'


def find_allheaders_fromhtml(trainpath, htmlpath, index):
    dict = {}
    with open(trainpath, 'r') as file:
        id = None
        for line in file:
            entity = line.split('\t')
            length = len(entity)
            if length > index:
                if entity[0] != id:
                    id = entity[0]
                    val = entity[index]
                    find_header_fromhtml(htmlpath, id, val, dict)
    print('----------------- over -----------------')
    print(sorted(dict.items(), key=lambda d: d[1], reverse=True))


# 20503293 建信基金管理有限责任公司
def find_header_fromhtml(htmlpath, id, val, dict):
    html = htmlpath + id + '.html'
    head = paser.show_header(html, val)
    print(id, val, head)
    if isinstance(head, str):
        head = re.sub('\s+', '', head)
        c = dict.get(head)
        if c is None:
            dict[head] = 1
        else:
            dict[head] = c + 1
        pass


find_allheaders_fromhtml(ht_trainpath, ht_htmlpath, 1)
