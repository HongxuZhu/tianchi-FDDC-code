import re

reg_number = '\d+(?:,\d{3}(?:,\d{1,3})*)*(?:\.\d+)?'

'((\d+)|(\d{1,3}\d{3}+\d{1,3})) (?:\.\d+)?'
pattern_number = re.compile(reg_number)

reg_number = '\d+(?:,\d{3})*(?:\.\d+)?'
pattern_number = re.compile(reg_number)

reg_price_DX = '[壹贰叁肆伍陆柒捌玖][零壹贰叁肆伍陆柒捌玖拾佰仟万亿]*[元圆]' \
               '(?:[整正]|[零壹贰叁肆伍陆柒捌玖]角(?:[零壹贰叁肆伍陆柒捌玖]分)?)?'  # ￥¥
pattern_price_DX = re.compile(reg_price_DX)


def norm_number(line):
    iters = pattern_number.findall(line)
    for iter in iters:
        # 归一化千分位数字表示法
        line = re.sub(iter, re.sub(',', '', iter), line)
        # print(iter)
    return line


print(norm_number('312.221   31   1,991       111,222,33 333,444.2'))
