from FDDC_PART2.preprocessing.QANetTrainFile import getDingZengUnion
import logging

dz_trainpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/dingzeng.train'
dz_testpath = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/submit_sample/train/dingzeng.test'

dzlog_path = 'dzanalyse.log'


def get_logger(log_file):
    logger = logging.getLogger(log_file)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


def eval_dz():
    dzlogger = get_logger(dzlog_path)
    trains = getDingZengUnion(dz_trainpath)
    tests = getDingZengUnion(dz_testpath)
    posid = posdx = possl = posje = possd = posrg = 0
    actid = actdx = actsl = actje = actsd = actrg = 0
    corid = cordx = corsl = corje = corsd = corrg = 0
    for id in trains.keys():
        train = trains.get(id)
        test = tests.get(id)
        train_pk = dz_withpk(train)
        test_pk = dz_withpk(test)

        for item in train:
            posid = pos(item.id, posid)
            posdx = pos(item.duixiang, posdx)
            possl = pos(item.shuliang, possl)
            posje = pos(item.jine, posje)
            possd = pos(item.suoding, possd)
            posrg = pos(item.rengou, posrg)
            dzlogger.info('id={},dx={},sl={},je={},sd={},rg={}'.format(item.id, item.duixiang, item.shuliang, item.jine, item.suoding, item.rengou))
        dzlogger.info('------------------------------以上为训练数据------------------------------')

        if test is None or len(train) != len(test):
            dzlogger.info('id={},数量不一致'.format(id))
        else:
            dzlogger.info('id={},数量一致'.format(id))

        if test is not None:
            for item in test:
                actid = act(item.id, actid)
                actdx = act(item.duixiang, actdx)
                actsl = act(item.shuliang, actsl)
                actje = act(item.jine, actje)
                actsd = act(item.suoding, actsd)
                actrg = act(item.rengou, actrg)
                dzlogger.info('id={},dx={},sl={},je={},sd={},rg={}'.format(item.id, item.duixiang, item.shuliang, item.jine, item.suoding, item.rengou))
        else:
            dzlogger.info('id={},未能识别'.format(id))

        for pk in train_pk.keys():
            train = train_pk.get(pk)
            test = test_pk.get(pk)
            if test is not None:  # 匹配主键
                corsl, truesl = cor(train.shuliang, test.shuliang, corsl)
                corje, trueje = cor(train.jine, test.jine, corje)
                corsd, truesd = cor(train.suoding, test.suoding, corsd)
                corrg, truerg = cor(train.rengou, test.rengou, corrg)
                # dzlogger.info('id={},dx={},sl={},je={},sd={},rg={}'.format(test.id, test.duixiang,
                #                                                            mask(test.shuliang, truesl),
                #                                                            mask(test.jine, trueje),
                #                                                            mask(test.suoding, truesd),
                #                                                            mask(test.rengou, truerg)))
            else:
                dzlogger.info('pk={},主键未能识别'.format(pk))
        dzlogger.info('------------------------------以上为预测数据------------------------------\n\n\n')

    disaccord = 0
    for id in tests.keys():
        train = trains.get(id)
        if train is None:
            disaccord += len(tests.get(id))
            dzlogger.info('id={},ID识别不一致'.format(id))

    dzlogger.info('posid={}, posdx={}, possl={}, posje={}, possd={}, posrg={}'.format(posid, posdx, possl, posje, possd, posrg))
    dzlogger.info('actid={}, actdx={}, actsl={}, actje={}, actsd={}, actrg={}'.format(actid, actdx, actsl, actje, actsd, actrg))
    dzlogger.info('corid={}, cordx={}, corsl={}, corje={}, corsd={}, corrg={}'.format(corid, cordx, corsl, corje, corsd, corrg))
    dzlogger.info('disaccord={}'.format(disaccord))

    p_sl, r_sl, f_sl = f1(corsl, possl, actsl)
    p_je, r_je, f_je = f1(corje, posje, actje)
    p_sd, r_sd, f_sd = f1(corsd, possd, actsd)
    p_rg, r_rg, f_rg = f1(corrg, posrg, actrg)
    dzlogger.info('SL: p={},r={},f1={}'.format(p_sl, r_sl, f_sl))
    dzlogger.info('JE: p={},r={},f1={}'.format(p_je, r_je, f_je))
    dzlogger.info('SD: p={},r={},f1={}'.format(p_sd, r_sd, f_sd))
    dzlogger.info('RG: p={},r={},f1={}'.format(p_rg, r_rg, f_rg))
    dzlogger.info('score={}'.format(score([f_sl, f_je, f_sd, f_rg])))


def mask(field, flag):
    if not flag:
        field = '_@_' + field
    return field


def dz_withpk(dzs):
    pks = {}
    if dzs is not None:
        for dz in dzs:
            pks[(dz.id, dz.duixiang)] = dz
    return pks


def recall(cor, pos):
    return float(cor / pos)


def precision(cor, act):
    return float(cor / act)


def pos(field, count):
    if field != 'fddcUndefined':
        count += 1
    return count


def act(field, count):
    if field != 'fddcUndefined':
        count += 1
    return count


def cor(train, test, count):
    flag = False

    if test == train:
        flag = True
        if train != 'fddcUndefined':
            count += 1

    return count, flag


def f1(cor, pos, act):
    p = precision(cor, act)
    r = recall(cor, pos)
    f = float((2 * p * r) / (p + r))
    return p, r, f


def score(f1s):
    score = 0
    for f1 in f1s:
        score += f1
    score /= (len(f1s) * 3)
    return score


eval_dz()
