# encoding=utf8

import os
import pickle

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
flags.DEFINE_integer("batch_size", 100, "batch size")
flags.DEFINE_float("lr", 0.001, "Initial learning rate")
flags.DEFINE_string("optimizer", "adam", "Optimizer for training")
flags.DEFINE_boolean("pre_emb", True, "Wither use pre-trained embedding")
flags.DEFINE_boolean("zeros", False, "Wither replace digits with zero")
flags.DEFINE_boolean("lower", True, "Wither lower case")
flags.DEFINE_integer("max_epoch", 50, "maximum training epochs")
flags.DEFINE_integer("steps_check", 100, "steps per checkpoint")

flags.DEFINE_string("ckpt_path", "ckpt/dingzeng/table_pk", "Path to save model")
flags.DEFINE_string("log_file", "ckpt/dingzeng/table_pk/train.log", "File for log")
flags.DEFINE_string("map_file", "ckpt/dingzeng/table_pk/maps.pkl", "file for maps")
flags.DEFINE_string("config_file", "ckpt/dingzeng/table_pk/config_file", "File for config")

flags.DEFINE_string("summary_path", "summary", "Path to store summaries")
flags.DEFINE_string("vocab_file", "vocab.json", "File for vocab")
flags.DEFINE_string("script", "conlleval", "evaluation script")
flags.DEFINE_string("result_path", "result", "Path for results")
flags.DEFINE_string("emb_file", os.path.join("data", "sgns.merge.char"), "Path for pre_trained embedding")
flags.DEFINE_string("train_file", os.path.join("data", "dz_pk_table.train"), "Path for train data")
flags.DEFINE_string("dev_file", os.path.join("data", "dz_pk_table.dev"), "Path for dev data")
flags.DEFINE_string("test_file", os.path.join("data", "test.test"), "Path for test data")

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

model_path = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/nlp/classification/dz_pk_cls_table.ftz'
dz_pk_cls_table_model = getModel(model_path)


def matchDuixiang(cell):
    label = predict(dz_pk_cls_table_model, cell)
    if label == '__label__dzpk':
        return True
    return False


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
        for id in dingzengs.keys():
            dzs = dingzengs[id]
            htmlpath = dz_htmlpath + id + '.html'

            rank = 6
            mod = int(id) % rank
            if mod == 0:
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

                                if matchDuixiang(valuecell):
                                    result = model.evaluate_line(sess, input_from_line(valuecell, char_to_id),
                                                                 id_to_tag)
                                    entities = result.get('entities')
                                    print(entities)


def main(_):
    evaluate()


if __name__ == "__main__":
    tf.app.run(main)
