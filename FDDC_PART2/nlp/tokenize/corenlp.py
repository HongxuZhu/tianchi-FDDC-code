from stanfordcorenlp import StanfordCoreNLP

# nlp = StanfordCoreNLP(r'G:\JavaLibraries\stanford-corenlp-full-2018-02-27')

sentence = '清华大学位于北京。'

with StanfordCoreNLP(r'/home/utopia/corpus/stanford-corenlp-full-2018-02-27', lang='zh') as nlp:
    print(nlp.word_tokenize(sentence))
    print(nlp.pos_tag(sentence))
    print(nlp.ner(sentence))
    print(nlp.parse(sentence))
    print(nlp.dependency_parse(sentence))