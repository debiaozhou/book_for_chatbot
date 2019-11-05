import os
import random
import re


DATA_PATH = 'XXXXXX'
CORPUS_FILE = 'corpus.txt'
PROCESSED_PATH = 'task_domain'
TESTSET_SIZE = 150
word_vec_dict = {}


def process_data():
    # 准备数据

    build_vocab('corpus.txt')
    token2id('train.enc')
    token2id('test.enc')


def build_vocab(filename):
    # 建立词表

    in_path = os.path.join(DATA_PATH, filename)
    index = 1
    with open(in_path, 'r', errors='ignore') as f:
        for line in f:
            if line:
                line = line.strip()
                words = line.split(' ')
                for word in words:
                    if not word_vec_dict.__contains__(word):
                        word_vec_dict[word] = index
                        index = index + 1
                        print('word=', word)
                        print('index=', index)


def token2id(file_name):
    # 将文本转换位向量

    in_path = os.path.join(PROCESSED_PATH, file_name)
    out_path = os.path.join(PROCESSED_PATH, file_name + '_ids')
    out_file = open(out_path, 'w')
    with open(in_path, 'r', errors='ignore') as f:
        for line in f:
            if line:
                line = line.strip()
                words = line.split(' ')
                for word in words:
                    if word_vec_dict.__contains__(word):
                        index = word_vec_dict[word]
                        out_file.write(str(index) + ' ')
                out_file.write('\n')


def question_categories():
    # 将语料库分成提问以及分类

    questions, categories = [], []
    file_path = os.path.join(DATA_PATH, CORPUS_FILE)
    print(CORPUS_FILE)
    with open(file_path, 'r', errors='ignore') as f:
        i = 0
        is_new_round = True
        is_category = True
        try:
            question_line = ""
            question_filled = False
            category = ""
            for line in f:
                if len(line) > 6 and line[:6] == "- - - ":
                    category = line[6:]
                    is_category = True
                elif line[:4] == "- - ":
                    is_new_round = True
                    is_category = False
                elif line[:2] == "- ":
                    is_new_round = False
                    is_category = False
                if not is_category:
                    if is_new_round:
                        question = line[4:]
                        questions.append(question)
                        question_line = question
                        question_filled = True
                        print(i, question)
                    else:
                        categories.append(category)
                        answer = line[2:]
                        if not question_filled:
                            questions.append(question_line)
                        else:
                            question_filled = False
                        question_line = answer
                        print(i, line)
                        i = i + 1
        except UnicodeDecodeError:
            print(i, line)
    assert len(questions) == len(categories)
    return questions, categories


def prepare_dataset(questions, categories):
    # 区分训练和测试数据

    make_dir(PROCESSED_PATH)
    test_ids = random.sample([i for i in range(len(questions))], TESTSET_SIZE)

    filenames = ['train.enc', 'train.dec', 'test.enc', 'test.dec']
    files = []
    for filename in filenames:
        files.append(open(os.path.join(PROCESSED_PATH, filename), 'w'))

    for i in range(len(questions)):
        if i in test_ids:
            files[2].write(questions[i])
            files[3].write(categories[i])
        else:
            files[0].write(questions[i])
            files[1].write(categories[i])

    for file in files:
        file.close()


def make_dir(path):
    # 新建目录

    try:
        os.mkdir(path)
    except OSError:
        pass


def prepare_raw_data():
    # 准备训练数据和测试数据

    questions, categories = question_categories()
    prepare_dataset(questions, categories)


if __name__ == '__main__':
    prepare_raw_data()
    process_data()
