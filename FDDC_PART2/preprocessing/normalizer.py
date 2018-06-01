import re
from decimal import Decimal

reg_number = '(\d+(?:,\d{3})*(?:\.\d+)?)(万元)?'
pattern_number = re.compile(reg_number)

reg_price_DX = '[壹贰叁肆伍陆柒捌玖][零壹贰叁肆伍陆柒捌玖拾佰仟万亿]*[元圆]' \
               '(?:[整正]|[零壹贰叁肆伍陆柒捌玖]角(?:[零壹贰叁肆伍陆柒捌玖]分)?)?'  # ￥¥
pattern_price_DX = re.compile(reg_price_DX)


def norm_number(line):
    iters = pattern_number.findall(line)
    for iter in iters:
        # 归一化千分位数字表示法
        num = iter[0].replace(',', '')
        iswan = True if iter[1] != '' else False
        if iswan:
            f = str((Decimal(num) * 10000).quantize(Decimal('0.000000')))
            line = line.replace(iter[0] + iter[1], f)
        else:
            dec = str(Decimal(num).quantize(Decimal('0.000000')))
            line = line.replace(iter[0], dec)

    return line

# print(norm_number('4444 44,444,333 444,444.3232 1,432,423.2万元'))
