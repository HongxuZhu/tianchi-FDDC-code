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
from FDDC_PART2_V1.preprocess.hetong.Trainfile_HT_ALL_NER_TEXT import levelText_without_table, getHeTongUnion
from FDDC_PART2_V1.rules.hetongPackage import org_ht

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
flags.DEFINE_integer("batch_size", 300, "batch size")
flags.DEFINE_float("lr", 0.001, "Initial learning rate")
flags.DEFINE_string("optimizer", "adam", "Optimizer for training")
flags.DEFINE_boolean("pre_emb", True, "Wither use pre-trained embedding")
flags.DEFINE_boolean("zeros", False, "Wither replace digits with zero")
flags.DEFINE_boolean("lower", True, "Wither lower case")
flags.DEFINE_integer("max_epoch", 50, "maximum training epochs")
flags.DEFINE_integer("steps_check", 100, "steps per checkpoint")

flags.DEFINE_string("ckpt_path", "ckpt/hetong/text_all", "Path to save model")
flags.DEFINE_string("map_file", "ckpt/hetong/text_all_maps.pkl", "file for maps")
flags.DEFINE_string("config_file", "ckpt/hetong/text_all_config_file", "File for config")
flags.DEFINE_string("log_file", "ht_text_all_train.log", "File for log")

flags.DEFINE_string("summary_path", "summary", "Path to store summaries")
flags.DEFINE_string("vocab_file", "vocab.json", "File for vocab")
flags.DEFINE_string("script", "conlleval", "evaluation script")
flags.DEFINE_string("result_path", "result", "Path for results")
flags.DEFINE_string("emb_file", os.path.join("data", "sgns.merge.char"), "Path for pre_trained embedding")
flags.DEFINE_string("test_file", os.path.join("data", "test.test"), "Path for test data")
flags.DEFINE_string("model_type", "idcnn", "Model type, can be idcnn or bilstm")

FLAGS = tf.app.flags.FLAGS
assert FLAGS.clip < 5.1, "gradient clip should't be too much"
assert 0 <= FLAGS.dropout < 1, "dropout rate between 0 and 1"
assert FLAGS.lr > 0, "learning rate must larger than zero"
assert FLAGS.optimizer in ["adam", "sgd", "adagrad"]

# 解决项目路径问题
os.chdir('/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/nlp/NER_IDCNN_CRF')
dz_trainpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/重大合同/hetong.train'
dz_htmlpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/重大合同/html/'

reg_isnum = '^\d+(\.\d+)?$'
pattern_isnum = re.compile(reg_isnum)

'''
model_path = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/nlp/classification/dz_att_cls_table.ftz'
dz_pk_cls_table_model = getModel(model_path)


def clsDuixiang(cell, threshold=0.00):
    label, score = predict(dz_pk_cls_table_model, cell)
    if label == '__label__nothing' and score >= threshold:
        return False
    return True
'''


def p_r(preset, truthset):
    t = len(preset.intersection(truthset))
    total_p = len(preset)
    total_r = len(truthset)
    return t, total_p, total_r


def evaluate(before=0):
    submit_path_ht = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/submit_sample/hetong.text'
    submit_path_file = open(submit_path_ht, 'a+')
    submit_path_file.write('公告id\t甲方\t乙方\t项目名称\t合同名称\t合同金额上限\t合同金额下限\t联合体成员\n')
    config = load_config(FLAGS.config_file)
    logger = get_logger(FLAGS.log_file)
    # limit GPU memory
    tf_config = tf.ConfigProto()
    tf_config.gpu_options.allow_growth = True
    with open(FLAGS.map_file, "rb") as f:
        char_to_id, id_to_char, tag_to_id, id_to_tag = pickle.load(f)
    with tf.Session(config=tf_config) as sess:
        model = create_model(sess, Model, FLAGS.ckpt_path, load_word2vec, config, id_to_char, logger)
        rootdir = '/home/utopia/corpus/FDDC_part2_data/FDDC_announcements_round1_test_a_20180605/重大合同/html/'
        list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
        for i in range(0, len(list)):
            htmlpath = os.path.join(rootdir, list[i])
            if os.path.isfile(htmlpath):
                print(htmlpath)
                s_arr = levelText_without_table(htmlpath)
                candidates = []
                for j in range(len(s_arr)):
                    sen = s_arr[j]
                    result = model.evaluate_line(sess, input_from_line(sen, char_to_id), id_to_tag)
                    entities = result.get('entities')
                    if len(entities) > 0:
                        for en in entities:
                            en['sid'] = j
                            en['pid'] = list[i]
                            candidates.append(en)
                org_ht(candidates, submit_path_file)
                print('-------------------------------------------------')


def main(_):
    evaluate()


if __name__ == "__main__":
    tf.app.run(main)
