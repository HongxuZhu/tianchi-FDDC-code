import re
import json
from bs4 import BeautifulSoup
import FDDC_PART2.preprocessing.normalizer as normalizer
# import FDDC_PART2.utils.dataframe as dfutil
import FDDC_PART2.preprocessing.autoTagging as tagger
import time, random, hashlib

hl = hashlib.md5()

reg_number = '([1-9]\d*(?:[,，]\d{3})*(?:\.\d+)?)( *万| *亿)?'
pattern_number = re.compile(reg_number)

# 公告id,增发对象,增发数量,增发金额,锁定期,认购方式
dz_trainpath = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/dingzeng.train'
dz_htmlpath_train = '/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/定增/html/'
dz_htmlpath_test = '/home/utopia/corpus/FDDC_part2_data/FDDC_announcements_round1_test_a_20180605/定增/html/'


# bug 未修复：句子比实际多
def levelText_withtable(htmlpath):
    soup = BeautifulSoup(open(htmlpath), 'lxml')
    pdf_title = soup.find_all('div', type='pdf')[0].attrs.get('title')
    dict_paragraphs = {'title': pdf_title, 'paragraphs': []}
    for paragraph in soup.find_all('div', type='paragraph'):
        dict_paragraph = {'context': ''}
        p_title = paragraph.attrs.get('title')
        if p_title is not None:
            updateDict(dict_paragraph, p_title)
        for content in paragraph.find_all('div', type='content'):
            c_title = content.attrs.get('title')
            if c_title is not None:
                updateDict(dict_paragraph, c_title)
            tables = content.find_all('table')
            # 假设训练数据中，text和table不同时存在于同一content内
            if len(tables) == 0:
                sen = content.get_text()
                updateDict(dict_paragraph, sen)
            else:
                for table in tables:
                    t_title = table.attrs.get('title')
                    if t_title is not None:
                        updateDict(dict_paragraph, t_title)
                    for tr in table.find_all('tr'):
                        td_arr = []
                        for td in tr.find_all('td'):
                            td_text = td.get_text()
                            if len(td_text) > 0:
                                td_arr.append(td_text)
                        updateDict(dict_paragraph, '║' + '╫'.join(td_arr) + '║')
        dict_paragraphs['paragraphs'].append(dict_paragraph)
    return dict_paragraphs


def updateDict(dict_paragraph, text):
    text = normalizer.norm_dz(text)
    if len(text) > 0:
        if text.endswith('。'):
            dict_paragraph['context'] = dict_paragraph.get('context') + text
        else:
            dict_paragraph['context'] = dict_paragraph.get('context') + text + '。'


def getDingZengUnion(trainpath):
    dzs = {}
    with open(trainpath, 'r') as file:
        for line in file:
            # line = line.encode('utf-8').decode('utf-8-sig')
            line = line[0:len(line) - 1]
            dz = tagger.getDingZeng(line)
            dzarray = dzs.get(dz.id)
            if dzarray is not None:
                dzs[dz.id].append(dz)
            else:
                dzs[dz.id] = [dz]
    return dzs


def QandA():
    # 增发对象(pk),增发数量,增发金额,锁定期,认购方式
    dingzengs = getDingZengUnion(dz_trainpath)
    js1 = {'version': '1.1', 'data': []}
    js2 = {'version': '1.1', 'data': []}
    rank = 100
    for id in dingzengs.keys():
        # id = '20503293'
        xxx = dingzengs[id]
        qaaaaaas = qas(xxx)
        html = levelText_withtable(dz_htmlpath_train + id + '.html')
        paragraphs = html['paragraphs']
        for paragraph in paragraphs:
            context = paragraph['context']
            tmpqas = []
            for xqas in qaaaaaas:
                for xqa in xqas:
                    answer = xqa['answers'][0]['text']
                    question = xqa['question']
                    qid = uuid()
                    if question.find('锁定期') != -1:  # 十二个月,三十六个月
                        continue
                    elif question.find('数量') != -1 or question.find('金额') != -1:
                        answers = find_answer(context, answer, True)
                    else:
                        answers = find_answer(context, answer, False)
                    if len(answers) > 0:
                        tmpqas.append({'answers': answers, 'question': question, 'id': qid})
            if len(tmpqas) > 0:
                paragraph['qas'] = tmpqas
        filters = []
        for item in paragraphs:
            qa_item = item.get('qas')
            if qa_item is not None:
                for xqas in qaaaaaas:
                    count = 0
                    for xqa in xqas:  # 一组标准答案
                        for qa in qa_item:
                            if qa['question'] == xqa['question']:
                                count += 1
                                break
                    if count >= 4:  # count >= len(xqas) 受限于内存，优选至少回答了一组所有问题的context
                        filters.append(item)
                        break
        if len(filters) > 0:
            html['paragraphs'] = filters
            mod = int(id) % rank
            if mod < 17:
                js1['data'].append(html)
            else:
                js2['data'].append(html)
            print(json.dumps(html, ensure_ascii=False))

    json.dump(js1, open('db1.json', 'w'), ensure_ascii=False)
    json.dump(js2, open('db2.json', 'w'), ensure_ascii=False)


def QandA_better(keep_limit):
    # 增发对象(pk),增发数量,增发金额,锁定期,认购方式
    dingzengs = getDingZengUnion(dz_trainpath)
    js1 = {'version': '1.1', 'data': []}
    js2 = {'version': '1.1', 'data': []}
    rank = 100
    for id in dingzengs.keys():
        xxx = dingzengs[id]
        qa_standard = qas(xxx)
        details = qa_standard['details']
        html = levelText_withtable(dz_htmlpath_train + id + '.html')
        paragraphs = html['paragraphs']

        for paragraph in paragraphs:
            context = paragraph['context']
            pkqas_confirm = []
            detailqas_confirm = []
            for pk in details.keys():
                pk_answers = find_answer(context, pk, False)
                if len(pk_answers) > 0:
                    detail_answers = []
                    count = 0
                    for detail in details[pk]:
                        answer = detail['answers'][0]['text']
                        question = detail['question']
                        answers = []
                        if question.find('锁定期') != -1:  # 十二个月,三十六个月
                            continue
                        elif question.find('数量') != -1 or question.find('金额') != -1:
                            answers = find_answer(context, answer, True)
                        else:
                            answers = find_answer(context, answer, False)
                        if len(answers) > 0:
                            detail_answers.append({'answers': answers, 'question': question, 'id': uuid()})
                            count += 1
                    if count >= keep_limit:
                        pkqas_confirm += pk_answers
                        detailqas_confirm += detail_answers

            if len(pkqas_confirm) > 0:
                paragraph['qas'] = detailqas_confirm
                paragraph['qas'].append({'answers': pkqas_confirm, 'question': '增发对象有哪些?', 'id': uuid()})

        filters = []
        for item in paragraphs:
            qa_item = item.get('qas')
            if qa_item is not None and len(qa_item) > 0:
                filters.append(item)

        if len(filters) > 0:
            html['paragraphs'] = filters
            mod = int(id) % rank
            if mod < 17:
                js1['data'].append(html)
            else:
                js2['data'].append(html)
            print(json.dumps(html, ensure_ascii=False))

    json.dump(js1, open('db1.json', 'w'), ensure_ascii=False)
    json.dump(js2, open('db2.json', 'w'), ensure_ascii=False)


def find_answer(context, answer, isNum):
    answer = answer.replace('(', '\(')
    answer = answer.replace(')', '\)')
    answer = answer.replace('[', '\[')
    answer = answer.replace(']', '\]')
    answers = []
    if isNum:  # 数字需要完全匹配，不能被部分包含
        numbers = pattern_number.finditer(context, re.I)
        for num in numbers:
            if num.group() == answer:
                begin, end = num.span()  # 返回每个匹配坐标
                answers.append({'answer_start': begin, 'text': answer})
    else:
        iters = re.finditer(answer, context, re.I)
        for iter in iters:
            begin, end = iter.span()  # 返回每个匹配坐标
            answers.append({'answer_start': begin, 'text': answer})
    '''
    strengthen = 3
    if len(answers) > 0 and len(answers) < strengthen:
        for i in range(strengthen - len(answers)):
            answers.append({'answer_start': answers[0]['answer_start'], 'text': answer})
    '''
    return answers


def qas(xxx):
    qas = {'details': {}}
    for x in xxx:
        xqas = []
        if x.shuliang != 'fddcUndefined':
            q2 = x.duixiang + '的增发数量是?'
            a2 = x.shuliang
            xqas.append(qa(a2, q2))

        if x.jine != 'fddcUndefined':
            q3 = x.duixiang + '的增发金额是?'
            a3 = x.jine
            xqas.append(qa(a3, q3))

        if x.suoding != 'fddcUndefined':
            q4 = x.duixiang + '的锁定期是?'
            a4 = x.suoding
            xqas.append(qa(a4, q4))

        if x.rengou != 'fddcUndefined':
            q5 = x.duixiang + '的认购方式是?'
            a5 = x.rengou
            xqas.append(qa(a5, q5))
        qas['details'][x.duixiang] = xqas
    return qas


def qa(a, q):
    qa = {'answers': [], 'question': q}
    answer = {'answer_start': -1, 'text': a}
    qa['answers'].append(answer)
    return qa


def catjson():
    with open('/home/utopia/github/QANet/datasets/squad/dev-v1.1.json') as f:
        js = json.load(f)
        for data in js['data']:
            title = data['title']
            for paragraph in data['paragraphs']:
                qas = paragraph['qas']
                for qa in qas:
                    id = qa['id']
                    question = qa['question']
                    answers = qa['answers']
                    for an in answers:
                        text = an['text']
                        # print(question, text)
                        if len(text) < 2:
                            print('len(text) < 2,', id, question, text)
                    if len(answers) == 0:
                        print('len(answers)==0,', id)
                if len(qas) == 0:
                    print('len(qas)==0,', title)


def uuid():
    string = str(time.time()) + str(random.random())
    hl.update(string.encode(encoding='utf-8'))
    return hl.hexdigest()

# QandA_better(3)
# print(levelText_withtable(dz_htmlpath_test + '10076'))
