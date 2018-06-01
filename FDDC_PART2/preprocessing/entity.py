# 此处定义3个实体类
import FDDC_PART2.preprocessing.normalizer as normalizer


class Contract:
    # 合同实体
    def __init__(self, trainline):
        fields = trainline.split('\t')
        length = len(fields)
        self.count = length  # 字段个数
        self.id = fields[0] if length > 0 and fields[0] != '' else 'fddcUndefined'
        self.jiafang = fields[1] if length > 1 and fields[1] != '' else 'fddcUndefined'
        self.yifang = fields[2] if length > 2 and fields[2] != '' else 'fddcUndefined'
        self.xiangmu = fields[3] if length > 3 and fields[3] != '' else 'fddcUndefined'
        self.hetong = fields[4] if length > 4 and fields[4] != '' else 'fddcUndefined'
        self.amount_u = normalizer.norm_number(fields[5]) if length > 5 and fields[5] != '' else 'fddcUndefined'
        self.amount_d = normalizer.norm_number(fields[6]) if length > 6 and fields[6] != '' else 'fddcUndefined'
        self.lianhe = fields[7] if length > 7 and fields[7] != '' else 'fddcUndefined'
