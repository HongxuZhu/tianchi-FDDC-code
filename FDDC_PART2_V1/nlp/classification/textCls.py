from __future__ import absolute_import
from __future__ import division
from __future__ import division, absolute_import, print_function
from __future__ import print_function
from __future__ import unicode_literals

from fastText import train_supervised
from fastText import load_model
from FDDC_PART2_V1.nlp.tokenize.cws import ltp_tokenize


def print_results(N, p, r):
    print("N\t" + str(N))
    print("P@{}\t{:.3f}".format(1, p))
    print("R@{}\t{:.3f}".format(1, r))


def getModel(path):
    return load_model(path)


def predict(model, text):
    text = ' '.join(ltp_tokenize(text))
    pre = model.predict(text)
    return pre[0][0], pre[1][0]


def train(t_data, v_data, model_path):
    model = train_supervised(
        input=t_data, epoch=25, lr=1.0, wordNgrams=3, verbose=2, minCount=1,
        loss="softmax"
    )
    print_results(*model.test(v_data))
    model.quantize(input=t_data, qnorm=True, retrain=True, cutoff=100000)
    print_results(*model.test(v_data))
    model.save_model(model_path)


if __name__ == "__main__":
    pass
    # model_path = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/nlp/classification/dz_pk_cls_table.ftz'
    # train_data = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/preprocess/dz_pk_cls_table.train'
    # valid_data = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/preprocess/dz_pk_cls_table.dev'
    # train(train_data, valid_data, model_path)
    #
    # trained = getModel(model_path)
    # print(predict(trained, '发行对象名称3、中航鑫港担保有限公司'))
    # print(predict(trained, '发行对象名称5、湖南湘投金天科技集团有限责任公司'))
    # print(predict(trained, '发行对象名称6、中国银河投资管理有限公司'))
    # print(predict(trained, '机构名称2广发基金管理有限公司'))
    # print(predict(trained, '机构名称3中航鑫港担保有限公司'))
    #
    # print(predict(trained, '占公司发行后总股份的比重(%)22.39%'))
    # print(predict(trained, '获配股数(万股)41,200'))
    # print(predict(trained, '占公司发行后总股份的比重(%)42.20%'))
    # print(predict(trained, '配售金额(万元)624,000'))
    # print(predict(trained, '占公司发行后总股份的比重(%)82.20%'))
