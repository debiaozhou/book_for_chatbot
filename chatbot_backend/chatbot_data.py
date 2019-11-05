import os
import random


DATA_PATH = 'XXXXXX'
CORPUS_FILE = 'corpus.txt'
PROCESSED_PATH = 'open_domain'

THRESHOLD = 2

TESTSET_SIZE = 150


def question_answers():
    # 将语料库分成提问以及回答

    questions, answers = [], []
    file_path = os.path.join(DATA_PATH, CORPUS_FILE)
    print(CORPUS_FILE)
    with open(file_path, 'r', errors='ignore') as f:
        i = 0
        is_new_round = True
        try:
            question_line = ""
            question_filled = False
            for line in f:
                if line[:4] == "- - ":
                    is_new_round = True
                elif line[:2] == "- ":
                    is_new_round = False
                if is_new_round:
                    question = line[4:]
                    questions.append(question)
                    question_line = question
                    question_filled = True
                    print(i, question)
                else:
                    answer = line[2:]
                    answers.append(answer)
                    if not question_filled:
                        questions.append(question_line)
                    else:
                        question_filled = False
                    question_line = answer
                    print(i, line)
                    i += 1
        except UnicodeDecodeError:
            print(i, line)
    assert len(questions) == len(answers)
    return questions, answers


def prepare_dataset(questions, answers):
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
            files[3].write(answers[i])
        else:
            files[0].write(questions[i])
            files[1].write(answers[i])

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

    questions, answers = question_answers()
    prepare_dataset(questions, answers)


if __name__ == '__main__':
    prepare_raw_data()