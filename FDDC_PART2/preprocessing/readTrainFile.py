import FDDC_PART2.preprocessing.htmlParser as paser

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


# 20503293 建信基金管理有限责任公司
def find_header_fromhtml(id, val):
    html = htmlpath + id + '.html'
    paser.show_header(html, val)


find_header_fromhtml('20503293', '建信基金管理有限责任公司')
