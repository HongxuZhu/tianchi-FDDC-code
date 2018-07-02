# encoding=utf8

import os
import pickle
import re
from decimal import Decimal

import tensorflow as tf
from bs4 import BeautifulSoup
from data_utils import load_word2vec, input_from_line
from model import Model
from utils import get_logger, create_model
from utils import load_config

from FDDC_PART2.preprocessing.QANetTrainFile import getDingZengUnion
from FDDC_PART2_V1.nlp.classification.textCls import getModel, predict
from FDDC_PART2_V1.preprocess.tableHandler import table2array

flags = tf.app.flags
flags.DEFINE_boolean("clean", False, "clean train folder")
flags.DEFINE_boolean("train", False, "Whether train the model")
# configurations for the model
flags.DEFINE_integer("seg_dim", 20, "Embedding size for segmentation, 0 if not used")
flags.DEFINE_integer("char_dim", 300, "Embedding size for characters")
flags.DEFINE_integer("lstm_dim", 100, "Num of hidden units in LSTM, or num of filters in IDCNN")
flags.DEFINE_string("tag_schema", "iobes", "tagging schema iobes or iob")

# configurations for training
flags.DEFINE_float("clip", 5, "Gradient clip")
flags.DEFINE_float("dropout", 0.5, "Dropout rate")
flags.DEFINE_integer("batch_size", 200, "batch size")
flags.DEFINE_float("lr", 0.001, "Initial learning rate")
flags.DEFINE_string("optimizer", "adam", "Optimizer for training")
flags.DEFINE_boolean("pre_emb", True, "Wither use pre-trained embedding")
flags.DEFINE_boolean("zeros", False, "Wither replace digits with zero")
flags.DEFINE_boolean("lower", True, "Wither lower case")
flags.DEFINE_integer("max_epoch", 50, "maximum training epochs")
flags.DEFINE_integer("steps_check", 100, "steps per checkpoint")

flags.DEFINE_string("ckpt_path", "ckpt/dingzeng/table_att", "Path to save model")
flags.DEFINE_string("map_file", "ckpt/dingzeng/table_att_maps.pkl", "file for maps")
flags.DEFINE_string("config_file", "ckpt/dingzeng/table_att_config_file", "File for config")
flags.DEFINE_string("log_file", "table_att_train.log", "File for log")

flags.DEFINE_string("summary_path", "summary", "Path to store summaries")
flags.DEFINE_string("vocab_file", "vocab.json", "File for vocab")
flags.DEFINE_string("script", "conlleval", "evaluation script")
flags.DEFINE_string("result_path", "result", "Path for results")
flags.DEFINE_string("emb_file", os.path.join("data", "sgns.merge.char"), "Path for pre_trained embedding")
flags.DEFINE_string("model_type", "idcnn", "Model type, can be idcnn or bilstm")
# flags.DEFINE_string("model_type", "bilstm", "Model type, can be idcnn or bilstm")

FLAGS = tf.app.flags.FLAGS
assert FLAGS.clip < 5.1, "gradient clip should't be too much"
assert 0 <= FLAGS.dropout < 1, "dropout rate between 0 and 1"
assert FLAGS.lr > 0, "learning rate must larger than zero"
assert FLAGS.optimizer in ["adam", "sgd", "adagrad"]

# 解决项目路径问题
os.chdir('/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/nlp/NER_IDCNN_CRF')

# 公告id,增发对象,发行方式,增发数量,增发金额,锁定期,认购方式
dz_trainpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/dingzeng.train'
dz_htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/html/'

model_path = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/nlp/classification/dz_att_cls_table.ftz'
dz_pk_cls_table_model = getModel(model_path)

reg_duixiang = '(' \
               '(关联|担保|发行|法定代表|获配|配售|认购|申购|投资|询价|报价|合伙|交易)' \
               '(对象|对方|方|人|者|机构|主体)' \
               '|股东)' \
               '(名称|全称|姓名|名册)?'  # $
pattern_duixiang = re.compile(reg_duixiang)

reg_isnum = '^\d+(\.\d+)?$'
pattern_isnum = re.compile(reg_isnum)


def clsDuixiang(cell, threshold=0.00):
    label, score = predict(dz_pk_cls_table_model, cell)
    if label == '__label__nothing' and score >= threshold:
        return False
    return True


def matchDuixiang(cell):
    if pattern_duixiang.search(cell) is not None:
        return True
    return False


def p_r(preset, truthset):
    t = len(preset.intersection(truthset))
    total_p = len(preset)
    total_r = len(truthset)
    return t, total_p, total_r


def evaluate():
    config = load_config(FLAGS.config_file)
    logger = get_logger(FLAGS.log_file)
    # limit GPU memory
    tf_config = tf.ConfigProto()
    tf_config.gpu_options.allow_growth = True
    with open(FLAGS.map_file, "rb") as f:
        char_to_id, id_to_char, tag_to_id, id_to_tag = pickle.load(f)
    with tf.Session(config=tf_config) as sess:

        model = create_model(sess, Model, FLAGS.ckpt_path, load_word2vec, config, id_to_char, logger)

        dingzengs = getDingZengUnion(dz_trainpath)
        TDX = T_PDX = T_RDX = 0
        TSL = T_PSL = T_RSL = 0
        TJE = T_PJE = T_RJE = 0
        for id in dingzengs.keys():
            dzs = dingzengs[id]
            htmlpath = dz_htmlpath + id + '.html'

            rank = 6
            mod = int(id) % rank
            if mod == 0:
                pre_dxs = set()
                pre_sls = set()
                pre_jes = set()
                soup = BeautifulSoup(open(htmlpath), 'lxml')
                tables = soup.find_all('table')
                for table in tables:  # 遍历所有table
                    cuts = table2array(table)  # 将table转为二维数组
                    for cut in cuts:  # 遍历规整行列数组
                        rows = len(cut)
                        cols = len(cut[0])
                        for row in range(rows):
                            for col in range(cols):

                                valuecell = cut[row][col]
                                topcell = cut[0][col]
                                leftcell = cut[row][0]

                                if row == 0 and col == 0:
                                    pass
                                elif row == 0 and col != 0:
                                    valuecell = leftcell + valuecell
                                elif row != 0 and col == 0:
                                    valuecell = topcell + valuecell
                                else:
                                    valuecell = topcell + leftcell + valuecell

                                if clsDuixiang(valuecell):
                                    result = model.evaluate_line(sess, input_from_line(valuecell, char_to_id),
                                                                 id_to_tag)
                                    entities = result.get('entities')
                                    for ent in entities:
                                        type = ent['type']
                                        word = ent['word']
                                        if type == 'DX':
                                            pre_dxs.add(word)
                                        elif type == 'SL_unit10k':
                                            if pattern_isnum.match(word):
                                                pre_sls.add(str((Decimal(word) * 10000)))
                                        elif type == 'SL_unit1':
                                            pre_sls.add(word)
                                        elif type == 'JE_unit10k':
                                            if pattern_isnum.match(word):
                                                pre_jes.add(str((Decimal(word) * 10000)))
                                        elif type == 'JE_unit1':
                                            pre_jes.add(word)
                                    # print(entities)

                truthdxs = set([dz.duixiang for dz in dzs if dz.duixiang != 'fddcUndefined'])
                truthsls = set([dz.shuliang for dz in dzs if dz.shuliang != 'fddcUndefined'])
                truthjes = set([dz.jine for dz in dzs if dz.jine != 'fddcUndefined'])
                tdx, total_pdx, total_rdx = p_r(pre_dxs, truthdxs)
                tsl, total_psl, total_rsl = p_r(pre_sls, truthsls)
                tje, total_pje, total_rje = p_r(pre_jes, truthjes)

                TDX += tdx
                T_PDX += total_pdx
                T_RDX += total_rdx

                TSL += tsl
                T_PSL += total_psl
                T_RSL += total_rsl

                TJE += tje
                T_PJE += total_pje
                T_RJE += total_rje

                print('TDX={},T_PDX={},T_RDX={}'.format(TDX, T_PDX, T_RDX))
                print('TSL={},T_PSL={},T_RSL={}'.format(TSL, T_PSL, T_RSL))
                print('TJE={},T_PJE={},T_RJE={}'.format(TJE, T_PJE, T_RJE))

                print(truthdxs)
                print(pre_dxs)
                print(truthsls)
                print(pre_sls)
                print(truthjes)
                print(pre_jes)
                print('---------------------------------------------------')


def main(_):
    evaluate()


if __name__ == "__main__":
    tf.app.run(main)
