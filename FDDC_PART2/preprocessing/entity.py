# 此处定义3个实体类
import FDDC_PART2.preprocessing.normalizer as normalizer


class Contract:
    # 合同实体
    def __init__(self, trainline):
        fields = trainline.split('\t')
        length = len(fields)
        self.count = 0  # 字段预期个数
        self.countActual = 0  # 字段实际个数

        if length > 0 and fields[0] != '':
            self.id = fields[0]
        else:
            self.id = 'fddcUndefined'

        if length > 1 and fields[1] != '':
            self.jiafang = fields[1]
            self.count += 1
        else:
            self.jiafang = 'fddcUndefined'

        if length > 2 and fields[2] != '':
            self.yifang = fields[2]
            self.count += 1
        else:
            self.yifang = 'fddcUndefined'

        if length > 3 and fields[3] != '':
            self.xiangmu = fields[3]
            self.count += 1
        else:
            self.xiangmu = 'fddcUndefined'

        if length > 4 and fields[4] != '':
            self.hetong = fields[4]
            self.count += 1
        else:
            self.hetong = 'fddcUndefined'

        if length > 5 and fields[5] != '':
            # self.amount_u = normalizer.norm_number(fields[5])
            self.amount_u = fields[5]
            self.count += 1
        else:
            self.amount_u = 'fddcUndefined'

        if length > 6 and fields[6] != '':
            # self.amount_d = normalizer.norm_number(fields[6])
            self.amount_d = fields[6]
            self.count += 1
        else:
            self.amount_d = 'fddcUndefined'

        if length > 7 and fields[7] != '':
            self.lianhe = fields[7]
            self.count += 1
        else:
            self.lianhe = 'fddcUndefined'

        self.labelDict = {'JF': 0, 'YF': 0, 'XM': 0, 'HT': 0, 'AU': 0, 'AD': 0, 'LH': 0}

    def setStatus(self, label):
        if self.labelDict[label] == 0:
            self.labelDict[label] = 1
            self.countActual += 1

    def desc(self):
        print('DESC html_ID= {} ,应有字段={},实有字段={},缺少{}个字段'
              .format(self.id, self.count, self.countActual, self.count - self.countActual))
        if self.labelDict['JF'] == 0 and self.jiafang != 'fddcUndefined':
            print('JF lost when makefile {}'.format(self.jiafang))
        if self.labelDict['YF'] == 0 and self.yifang != 'fddcUndefined':
            print('YF lost when makefile {}'.format(self.yifang))
        if self.labelDict['XM'] == 0 and self.xiangmu != 'fddcUndefined':
            print('XM lost when makefile {}'.format(self.xiangmu))
        if self.labelDict['HT'] == 0 and self.hetong != 'fddcUndefined':
            print('HT lost when makefile {}'.format(self.hetong))
        if self.labelDict['AU'] == 0 and self.amount_u != 'fddcUndefined':
            print('AU lost when makefile {}'.format(self.amount_u))
        if self.labelDict['AD'] == 0 and self.amount_d != 'fddcUndefined':
            print('AD lost when makefile {}'.format(self.amount_d))
        if self.labelDict['LH'] == 0 and self.lianhe != 'fddcUndefined':
            print('LH lost when makefile {}'.format(self.lianhe))
        print('----------------- over -----------------')
