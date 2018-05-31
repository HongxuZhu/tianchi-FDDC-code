import re

import FDDC_PART2.preprocessing.htmlParser as parser
from FDDC_PART2.preprocessing.entity import Contract

# 20315972
# 宁夏汉尧石墨烯储能材料科技有限公司
# 湖南百利工程科技股份有限公司
# 锂离子电池石墨烯三元正极材料及导电浆料
# 锂离子电池石墨烯三元正极材料及导电浆料项目智能产线设计建造合同
# 1295000000
# 1295000000
# 北京高能时代环境技术股份有限公司

trainline = '20315972	宁夏汉尧石墨烯储能材料科技有限公司	湖南百利工程科技股份有限公司	锂离子电池石墨烯三元正极材料及导电浆料	锂离子电池石墨烯三元正极材料及导电浆料项目智能产线设计建造合同	1295000000	1295000000	北京高能时代环境技术股份有限公司'


def tag_text(htmlpath, trainline):
    s_arr = parser.levelText(htmlpath)
    contract = Contract(trainline)
    for s in s_arr:
        mask_contract(s, contract)


def mask_contract(line_source, contract):
    # 假设各字段之间不相交
    mask_contract_field(line_source, contract.jiafang, 'JIA')
    mask_contract_field(line_source, contract.yifang, 'YI')
    mask_contract_field(line_source, contract.xiangmu, 'XM')
    mask_contract_field(line_source, contract.hetong, 'HT')
    mask_contract_field(line_source, contract.amount_u, 'AU')
    mask_contract_field(line_source, contract.amount_d, 'AD')
    mask_contract_field(line_source, contract.lianhe, 'LH')


def mask_contract_field(line_source, val, label):
    if val != 'fddcUndefined':
        iters = re.finditer(val, line_source)
        for iter in iters:
            begin, end = iter.span()  # 返回每个匹配坐标
            print('label={},begin={},end={},val={},line={}'.format(label, begin, end, val, line_source))


tag_text('/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/重大合同/html/20315972.html', trainline)
