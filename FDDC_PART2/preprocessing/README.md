# import step record

mkdir submit_sample

unzip FDDC_announcements_round1_train_20180518.zip

unzip FDDC_announcements_round1_test_a_20180524.zip

unzip FDDC_announcements_submit_sample_20180524.zip -d submit_sample/

pip3 install stanfordcorenlp

path1:/home/utopia/corpus/stanford-corenlp-full-2018-02-27

path2:stanford-chinese-corenlp-2018-02-27-models.jar in path1

pip3 install html5lib

pip3 install BeautifulSoup4

pip3 install lxml

sudo pip3 install pandas

cd /home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2/expand/NER_IDCNN_CRF

python3 /usr/local/bin/tensorboard --logdir=ckpt

python3 main.py --train=True --clean=True --model_type=bilstm/idcnn

in pycharm:

search everywhere -> configurations ->Edit configurations
LD_LIBRARY_PATH=/usr/local/cuda-9.0/lib64
PYTHONPATH=/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2_V1/nlp/NER_IDCNN_CRF

gedit ~/.bashrc

export PYTHONPATH=$PYTHONPATH:/home/utopia/github/models/research:/home/utopia/github/models/research/slim:/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2

source ~/.bashrc

echo $PYTHONPATH

cd /home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2/expand/NER_IDCNN_CRF

python3 predictor.py

sudo pip3 install pdfminer.six

$ wget https://github.com/facebookresearch/fastText/archive/v0.1.0.zip
$ unzip v0.1.0.zip
$ cd fastText-0.1.0
$ sudo make
$ git clone https://github.com/facebookresearch/fastText.git
$ cd fastText
$ sudo pip3 install .