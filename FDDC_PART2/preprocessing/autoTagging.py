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
trainfile = ''


def tag_text(htmlpath, trainline, makefile):
    s_arr = parser.levelText_withtable(htmlpath)
    contract = Contract(trainline)
    for s in s_arr:
        mask_contract(s, contract, makefile)
    if contract.count != contract.countActual:
        contract.desc()
        pass


# 假设各字段之间不相交，对于金额上下限等情况考虑加入附加字段
def mask_contract(line_source, contract, makefile):
    tag_arr = ['O'] * len(line_source)
    mask_contract_field(line_source, contract.jiafang, tag_arr, 'JF', contract)
    mask_contract_field(line_source, contract.yifang, tag_arr, 'YF', contract)
    mask_contract_field(line_source, contract.xiangmu, tag_arr, 'XM', contract)
    mask_contract_field(line_source, contract.hetong, tag_arr, 'HT', contract)
    mask_contract_field(line_source, contract.amount_u, tag_arr, 'AU', contract)
    mask_contract_field(line_source, contract.amount_d, tag_arr, 'AD', contract)
    mask_contract_field(line_source, contract.lianhe, tag_arr, 'LH', contract)
    for i in range(len(line_source)):
        makefile.write(line_source[i] + ' ' + tag_arr[i] + '\n')
    makefile.write('\n')
    # print(line_source)
    # print(tag_arr)


def mask_contract_field(line_source, val, tag_arr, label, contract):
    if val != 'fddcUndefined':
        val = val.replace('(', '\(')
        val = val.replace(')', '\)')
        val = val.replace('[', '\[')
        val = val.replace(']', '\]')
        iters = re.finditer(val, line_source, re.I)
        for iter in iters:
            begin, end = iter.span()  # 返回每个匹配坐标
            contract.setStatus(label)
            tag_arr[begin] = 'B-' + label
            for index in range(begin + 1, end):
                tag_arr[index] = 'I-' + label


def test():
    contract = Contract(trainline)
    mask_contract(trainline, contract)

# tag_text('/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/重大合同/html/20315972.html', trainline)
# test()
