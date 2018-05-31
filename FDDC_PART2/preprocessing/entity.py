# 此处定义3个实体类

class Contract:
    # 合同实体
    def __init__(self, trainline):
        fields = trainline.split('\t')
        length = len(fields)
        self.id = fields[0] if length > 0 else 'fddcUndefined'
        self.jiafang = fields[1] if length > 1 else 'fddcUndefined'
        self.yifang = fields[2] if length > 2 else 'fddcUndefined'
        self.xiangmu = fields[3] if length > 3 else 'fddcUndefined'
        self.hetong = fields[4] if length > 4 else 'fddcUndefined'
        self.amount_u = fields[5] if length > 5 else 'fddcUndefined'
        self.amount_d = fields[6] if length > 6 else 'fddcUndefined'
        self.lianhe = fields[7] if length > 7 else 'fddcUndefined'
