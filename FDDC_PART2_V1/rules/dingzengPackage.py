import re
from decimal import Decimal

# 前，中，后
# reg_duixiang1 = '(报价|询价|承诺|持有|担保|发行|股东|关联|合伙|获配|交易|配售|配套|认购|申购|投资|委托|邀请|法定代表)' \
reg_duixiang0 = '(发行|获配|交易|配售|配套|认购|投资)' \
                '(机构|者|方|人|对象|对方|对手|单位|主体|产品)' \
                '(名称|全称|简称|构成|名册|姓名)?[：:]?$'
pattern_duixiang0 = re.compile(reg_duixiang0)

reg_duixiang1 = '(报价|询价|承诺|持有|关联|合伙|委托|邀请)' \
                '(机构|者|方|人|对象|对方|对手|单位|主体|产品)' \
                '(名称|全称|简称|构成|名册|姓名)?[：:]?$'
pattern_duixiang1 = re.compile(reg_duixiang1)

# reg_duixiang2 = '(产品|单位|公司|机构|自然人|企业|账户)?(名称|全称|简称|构成|名册|姓名)'
reg_duixiang2 = '(产品|单位|公司|机构|自然人|企业|账户)?(名称|全称|简称|构成|名册|姓名)[：:]?$'
pattern_duixiang2 = re.compile(reg_duixiang2)

reg_duixiang_neg = '股东|项目'
pattern_duixiang_neg = re.compile(reg_duixiang_neg)

# duixiangs = ['标的资产', '公司', '股东', '机构', '一致行动人', '乙方', '员工持股计划']
duixiangs = ['标的资产', '公司', '机构', '一致行动人', '乙方', '员工持股计划']

# 动词，副词，名词，量词，单位
reg_shuliang1 = '(配售|获配|获售|限售|发行|发售|发股|认购|持有|持股|变动|交易|调整|申购|申报)(后|之后)?' \
                '(股份|股本|证券|股票|A股|新股|股数)?(总数|总额|数|数量)?(\(?万?[股只]\)?)?$'
pattern_shuliang1 = re.compile(reg_shuliang1)

reg_shuliang2 = '(股份|股本|证券|股票|A股|新股|股数)(总数|总额|数|数量)?(\(?万?[股只]\)?)?$'
pattern_shuliang2 = re.compile(reg_shuliang2)

# 动词，名词，单位
reg_jine = '(((出资|担保|获配|募集|配售|认购|认缴|申购|投资)(资金)?(额|金额|总额|资金)(/?\(?万?元\)?)?)|((金额|总额)(/?\(?万?元\)?)))$'
pattern_jine = re.compile(reg_jine)

# 动词，名词，单位
reg_suoding = '(((限售|锁定|流通)(时间|期|期限|月份)(\(?个?月\)?)?)|(\(个?月\)))$'
pattern_suoding = re.compile(reg_suoding)

# 动词，名词
reg_rengou = '^(((认购|出资|结算|分配|支付|对价)(方式|形式))|(现金|认购))$'
pattern_rengou = re.compile(reg_rengou)

reg_isnum = '\d+(\.\d+)?'
pattern_isnum = re.compile(reg_isnum)


def reg_dx_table(text):
    search0 = pattern_duixiang0.search(text)
    basescore = 0
    if text.find('对象') != -1:
        basescore += 0.5
    if pattern_duixiang_neg.search(text) is not None:
        basescore -= 1

    if search0 is not None:
        return 3 + basescore
    else:
        search1 = pattern_duixiang1.search(text)
        if search1 is not None:
            return 2 + basescore
        else:
            search2 = pattern_duixiang2.search(text)
            if search2 is not None:
                return 1 + basescore
            else:
                if text in duixiangs:
                    return 1 + basescore
                else:
                    return basescore


def reg_sl_table(text):
    search1 = pattern_shuliang1.search(text)
    if search1 is not None:
        return True
    else:
        search2 = pattern_shuliang2.search(text)
        if search2 is not None:
            start = search2.span()[0]
            if start != 0:
                qian = text[start - 1:start]
                if qian != '前':
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False


def reg_je_table(text):
    search = pattern_jine.search(text)
    if search is not None:
        return True
    else:
        return False


def reg_sd_table(text):
    search = pattern_suoding.search(text)
    if search is not None:
        return True
    else:
        return False


def reg_rg_table(text):
    search = pattern_rengou.search(text)
    if search is not None:
        return True
    else:
        return False


class dz_tmp():
    def __init__(self, id):
        self.countActual = 0  # 字段实际个数
        self.id = id
        self.duixiang = 'fddcUndefined'
        self.shuliang = 'fddcUndefined'
        self.jine = 'fddcUndefined'
        self.suoding = 'fddcUndefined'
        self.rengou = 'fddcUndefined'

    def desc(self):
        print('HTMLID= {} |DX= {} |数量= {} |金额= {} |锁定= {} |认购= {} '
              .format(self.id, self.duixiang, self.shuliang, self.jine, self.suoding, self.rengou))


def orgdz_byrow(id, table, startrow, rows, cols):
    dz_tmp_list = []
    for row in range(startrow + 1, rows):
        tmp = dz_tmp(id)
        for col in range(cols):
            tag = table[startrow][col]
            cell = table[row][col]
            numflag = pattern_isnum.search(cell)
            if reg_dx_table(tag):
                if tmp.duixiang == 'fddcUndefined' and cell not in ['合计', '总计', '汇总', '小计']:
                    tmp.duixiang = cell
                    tmp.countActual += 1
                continue
            if reg_sl_table(tag) and numflag is not None:
                # if tmp.shuliang == 'fddcUndefined':
                num = numflag.group()
                if tag.find('万') != -1:
                    tmp.shuliang = str((Decimal(num) * 10000))
                else:
                    tmp.shuliang = num
                tmp.countActual += 1
                continue
            if reg_je_table(tag) and numflag is not None:
                # if tmp.jine == 'fddcUndefined':
                num = numflag.group()
                if tag.find('万') != -1:
                    tmp.jine = str((Decimal(num) * 10000))
                else:
                    tmp.jine = num
                tmp.countActual += 1
                if float(tmp.jine) == 0:  # 明确0元剔除
                    break
                continue
            if reg_sd_table(tag) and numflag is not None:
                # if tmp.suoding == 'fddcUndefined':
                num = numflag.group()
                tmp.suoding = num
                tmp.countActual += 1
                continue
            if reg_rg_table(tag):
                # if tmp.rengou == 'fddcUndefined':
                tmp.rengou = cell
                tmp.countActual += 1
                continue
        if tmp.duixiang != 'fddcUndefined' and len(tmp.duixiang) > 1 and tmp.countActual > 1:
            dz_tmp_list.append(tmp)

    effective = 0
    for tmp in dz_tmp_list:
        effective += tmp.countActual

    return effective, dz_tmp_list


# def table_tag_byrow(id, table):
#     rows = len(table)
#     cols = len(table[0])
#     tagcount_dict = {}
#     for row in range(rows):
#         tagcount = 0
#         for col in range(cols):
#             cell = table[row][col]
#             if reg_dx_table(cell):
#                 tagcount += 1
#                 continue
#             if reg_sl_table(cell):
#                 tagcount += 1
#                 continue
#             if reg_je_table(cell):
#                 tagcount += 1
#                 continue
#             if reg_sd_table(cell):
#                 tagcount += 1
#                 continue
#             if reg_rg_table(cell):
#                 tagcount += 1
#                 continue
#         tagcount_dict[row] = tagcount
#
#     paixu = list(sorted(tagcount_dict.items(), key=lambda d: d[1], reverse=True))
#     startrow = paixu[0][0]
#
#     return orgdz_byrow(id, table, startrow, rows, cols)

def table_tag_byrow(id, table):
    rows = len(table)
    cols = len(table[0])
    tagcount_dict = {}
    for row in range(rows):
        for col in range(cols):
            cell = table[row][col]
            weight = reg_dx_table(cell)
            if weight > 0:
                tagcount_dict[row] = weight, cell
                break

    paixu = list(sorted(tagcount_dict.items(), key=lambda d: d[1], reverse=True))
    if len(paixu) > 0:
        startrow = paixu[0][0]
        weight = paixu[0][1][0]
        tag = paixu[0][1][1]
        effective, dz_tmp_list = orgdz_byrow(id, table, startrow, rows, cols)
        return weight, effective, dz_tmp_list, tag
    else:
        return 0, None, None, None
