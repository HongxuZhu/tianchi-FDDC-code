import re

# select count(distinct(`合同名称`)) from hetong
# where `合同名称` REGEXP '合同|协议';
# 命中率=882/897
reg_hetong = '签[订署]\S+(合同|协议)'
pattern_hetong = re.compile(reg_hetong)

# select count(distinct(`项目名称`)) from hetong
# where `项目名称` REGEXP '项目|工程|设备|系统|施工|建设|标段';
# 命中率=2055/2154
reg_xiangmu = '(本公司为|收到|中标|确定|承建|工程名称|项目名称)\S+(项目|工程|设备|系统|施工|建设|标段)'
pattern_xiangmu = re.compile(reg_xiangmu)

# '(金|合同|总)额'
# '(中标|总|报|造|合同|定|估|成交)价'
# '[付货价]款'
# '(共计|总计|概算|结算|人民币|投资|总收入|大写|价格)'
reg_jine = '((金|合同|总)额)' \
           '|((中标|总|报|造|合同|定|估|成交)价)' \
           '|([付货价]款)' \
           '|((共计|总计|概算|结算|人民币|总收入|大写|价格))'
pattern_jine = re.compile(reg_jine)

'''
联合体，甲方，乙方关键词最好互斥
'''
reg_lianhe = '联合体|共同'
pattern_lianhe = re.compile(reg_lianhe)

reg_yifang = '董事会|子公司|候选人|供应商|以下简称|中标|投标|乙方|承包人|卖方'
pattern_yifang = re.compile(reg_yifang)

reg_jiafang = '收到|通知|甲方|买方|业主|委托|采购|购买|投资|招标|发出|发布|发包'
pattern_jiafang = re.compile(reg_jiafang)


def filter_ht(text):
    if pattern_hetong.search(text) is not None:
        return 1
    return 0


def filter_lh(text):
    if pattern_lianhe.search(text) is not None:
        return 1
    return 0


def filter_xm(text):
    if pattern_xiangmu.search(text) is not None:
        return 1
    return 0


def org_ht(candidates, submit_path_file):
    # pid,YF,JY为联合主键，YF不为空
    types = {'JF': [], 'YF': [], 'XM': [], 'HT': [], 'AU': [], 'AD': [], 'LH': []}
    if len(candidates) > 0:
        pid = candidates[0]['pid']
        for can in candidates:
            type = can.get('type')
            types[type].append(can)
        jfs = types['JF']
        yfs = types['YF']
        xms = types['XM']
        hts = types['HT']
        aus = types['AU']
        ads = types['AD']
        lhs = types['LH']

        yfset = set()
        for yf in yfs:
            yfset.add(yf['word'])

        pair_jf = findNearestPair(jfs, yfs)
        pair_xm = findNearestPair(xms, yfs)
        pair_ht = findNearestPair(hts, yfs)
        pair_au = findNearestPair(aus, yfs)
        pair_ad = findNearestPair(ads, yfs)
        pair_lh = findNearestPair(lhs, yfs)
        for yfword in yfset:  # 因为乙方不为空，所以先确定乙方
            near_jf = find_near(pair_jf, yfword)
            near_xm = find_near(pair_xm, yfword)
            near_ht = find_near(pair_ht, yfword)
            near_au = find_near(pair_au, yfword)
            near_ad = find_near(pair_ad, yfword)
            near_lh = find_near(pair_lh, yfword)

            if near_au == '':
                near_au = near_ad
            if near_ad == '':
                near_ad = near_au
            if near_au < near_ad:
                tmp = near_ad
                near_ad = near_au
                near_au = tmp

            ht = []
            ht.append(pid)
            ht.append(near_jf)
            ht.append(yfword)
            ht.append(near_xm)
            ht.append(near_ht)
            ht.append(near_au)
            ht.append(near_ad)
            ht.append(near_lh)
            submit_ht(ht, submit_path_file)


def find_near(pairs, word):
    for pair in pairs:
        if pair[1] == word:
            return pair[0]
            # return re.sub(',', '', pair[0])
    return ''


def submit_ht(ht, submit_path_file):
    pid = ht[0]
    near_jf = ht[1]
    yfword = ht[2]
    near_xm = ht[3]
    near_ht = ht[4]
    near_au = ht[5]
    near_ad = ht[6]
    near_lh = ht[7]
    print('pid={},JF={},YF={},XM={},HT={},AU={},AD={},LH={}'
          .format(pid, near_jf, yfword, near_xm, near_ht, near_au, near_ad, near_lh))

    line = '\t'.join(ht) + '\n'
    submit_path_file.write(line)


def findNearestPair(subTypesTarget, subTypesPK):
    list = []
    for sk in subTypesPK:
        pk = sk['word']
        if len(subTypesTarget) == 0:
            list.append(('', pk, 100000, 100000))
        else:
            for st in subTypesTarget:
                if pk != st['word']:
                    sid_distance = abs(sk['sid'] - st['sid'])
                    word_distance = min(abs(sk['start'] - st['end']), abs(sk['end'] - st['start']))
                    target = st['word']
                    list.append((target, pk, sid_distance, word_distance))
    list.sort(key=lambda x: (x[2], x[3]))

    pairs = []
    pkset = set()
    tergset = set()
    for candidate in list:
        temp_t = candidate[0]
        temp_s = candidate[1]
        if temp_s not in pkset and temp_t not in tergset:
            pkset.add(temp_s)
            tergset.add(temp_t)
            pairs.append((temp_t, temp_s))
    return pairs
