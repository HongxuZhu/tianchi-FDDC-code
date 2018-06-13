import re
from decimal import Decimal

# reg_number = '(\d+(?:,\d{3})*(?:\.\d+)?)( *万美?元| *亿美?元)?'
# reg_number = '(\d+(?:[,，]\d{3})*(?:\.\d+)?)( *万[美港]?元| *亿[美港]?元)?'
reg_number = '([1-9]\d*(?:[,，]\d{3})*(?:\.\d+)?)( *万[美欧港]?元| *亿[美欧港]?元)?'
pattern_number = re.compile(reg_number)

reg_price_DX = '[壹贰叁肆伍陆柒捌玖][零壹贰叁肆伍陆柒捌玖拾佰仟万亿]*[元圆]' \
               '(?:[整正]|[零壹贰叁肆伍陆柒捌玖]角(?:[零壹贰叁肆伍陆柒捌玖]分)?)?'  # ￥¥
pattern_price_DX = re.compile(reg_price_DX)

reg_xm_1 = '“[^“”]+”项目'
pattern_xm_1 = re.compile(reg_xm_1)


def norm_number_2bit(line):
    try:
        iters = pattern_number.findall(line)
        for iter in iters:
            # 归一化千分位数字表示法
            num = re.sub(',|，', '', iter[0])
            iswan = True if iter[1] != '' else False
            if iswan:
                if iter[1].find('万') != -1:
                    f = str((Decimal(num) * 10000).quantize(Decimal('0.00')))
                else:
                    f = str((Decimal(num) * 100000000).quantize(Decimal('0.00')))
                if f.endswith('.00'):
                    f = f[0:len(f) - 3]
                elif f.endswith('0'):
                    f = f[0:len(f) - 1]
                # f = str((Decimal(num) * 10000))
                line = line.replace(iter[0] + iter[1], f)
            else:
                dec = str(Decimal(num).quantize(Decimal('0.00')))
                if dec.endswith('.00'):
                    dec = dec[0:len(dec) - 3]
                elif dec.endswith('0'):
                    dec = dec[0:len(dec) - 1]
                # dec = str(Decimal(num))
                line = line.replace(iter[0], dec)
    except:
        pass
    return line


def norm_number(line):
    iters = pattern_number.findall(line)
    for iter in iters:
        # 归一化千分位数字表示法
        num = re.sub(',|，', '', iter[0])
        iswan = True if iter[1] != '' else False
        if iswan:
            if iter[1].find('万') != -1:
                f = str((Decimal(num) * 10000).quantize(Decimal('0.0')))
            else:
                f = str((Decimal(num) * 100000000).quantize(Decimal('0.0')))
            if f.endswith('.0'):
                f = f[0:len(f) - 2]
            line = line.replace(iter[0] + iter[1], f)
        else:
            dec = str(Decimal(num).quantize(Decimal('0.0')))
            if dec.endswith('.0'):
                dec = dec[0:len(dec) - 2]
            line = line.replace(iter[0], dec)
    return line


def norm_xm(line):
    iters = pattern_xm_1.findall(line)
    for iter in iters:
        line = re.sub(iter, re.sub('“|”', '', iter), line)
    return line


def norm_text_correct(line):
    bs = line.split(' ')
    clean = re.sub('\s+', '', bs[0])
    for i in range(1, len(bs)):
        s = re.sub('\s+', '', bs[i])
        if re.match('[a-z]+', s, re.I):
            clean += (' ' + s)
        else:
            clean += s
    clean = re.sub('/|"', '', clean)
    clean = re.sub('（', '(', clean)
    clean = re.sub('）', ')', clean)
    return clean


def norm_text(line):
    clean = re.sub('\s+', '', line)
    clean = re.sub('/|"', '', clean)
    clean = re.sub('（', '(', clean)
    clean = re.sub('）', ')', clean)
    clean = re.sub('～', '~', clean)
    return clean


def norm(line):
    line = norm_text(line)
    line = norm_number_2bit(line)
    line = norm_xm(line)
    return line
# print(norm_number('金乡县垃圾焚烧发电厂BOT特许经营项目总投资42,276.00 万元，垃圾处理补贴费：60.00元/吨/人民币。建设周期为18个月。'))
# print(norm_number('黄山至祁门、宣城至宁国、阜阳至新蔡高速公路机电与配电工程以及阜阳至周集、周集至六安高速公路配电工程 HQJD-02、HQPD-01、FZZLPD-01 标段和HQPD-02、FXJD-01 标段'))
# print(norm_xm('“青州市智能交通及平安城市系统建设工程”项目'))
# print(norm_text('愎度 Abhijeet Projects Limited'))
