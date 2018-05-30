import FDDC_PART2.preprocessing.htmlParser as paser
import re

trainpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/dingzeng.train'
htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/html/'


# show 增发对象 header
def show_obj_header():
    with open(trainpath, 'r') as file:
        for line in file:
            entity = line.split('\t')
            # 公告id,增发对象,发行方式,增发数量,增发金额,锁定期,认购方式
            id = entity[0]
            obj = entity[1]
            # pub = entity[2]
            # num = entity[3]
            # amount = entity[4]
            # lock = entity[5]
            # sub = entity[6]
            print(id, obj)


def find_allheaders_fromhtml():
    dict = {}
    with open(trainpath, 'r') as file:
        id = None
        for line in file:
            entity = line.split('\t')
            if entity[0] != id:
                id = entity[0]
                obj = entity[1]
                find_header_fromhtml(id, obj, dict)
    print('----------------- over -----------------')
    print(sorted(dict.items(), key=lambda d: d[1], reverse=True))
    # bid_org_dict = sorted(bid_org_dict.items(), key=lambda i: i[1][2], reverse=True)


# 20503293 建信基金管理有限责任公司
def find_header_fromhtml(id, val, dict):
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


find_allheaders_fromhtml()
