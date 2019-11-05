import os


DATA_PATH = 'XXXXXX'
CORPUS_FILE = 'sentiment_XS_30k.txt'
TEST_FILE = 'sentiment_XS_test.txt'
PROCESSED_PATH = 'emotion_domain'
word_vec_dict = {}
words_to_be_removed = []


def process_data():
    # 准备数据

    index = build_vocab('train.enc', 1)
    index = build_vocab('test.enc', index)
    token2id('train.enc')
    token2id('test.enc')


def build_vocab(filename, index):
    # 建立词表

    in_path = os.path.join(PROCESSED_PATH, filename)
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
    return index


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


def sentence_categories(file_name):
    # 将语料库分成句子以及情感分类

    sentences, categories = [], []
    file_path = os.path.join(DATA_PATH, file_name)
    with open(file_path, 'r', errors='ignore') as f:
        for line in f:
            if line:
                segments = line.split(',')
                assert(len(segments) == 2)
                category = segments[0]
                sentence = segments[1]
                # 删除停用词
                sentence = sentence.strip()
                assert(not sentence == '')
                words = sentence.split(' ')
                sentence = ''
                for word in words:
                    if word not in words_to_be_removed:
                        if sentence == '':
                            sentence = word
                        else:
                            sentence = sentence + ' ' + word
                sentence = sentence.strip()
                if not sentence == '':
                    sentences.append(sentence + '\n')
                    if category == 'positive':
                        category = 0
                    else:
                        category = 1
                    categories.append(str(category) + '\n')
                    if sentence == '':
                        print('category=', category, ' sentence=', sentence)
    assert len(sentences) == len(categories)
    return sentences, categories


def prepare_dataset(is_train, sentences, categories):
    # 区分训练和测试数据

    make_dir(PROCESSED_PATH)
    filenames = []
    if is_train:
        filenames.append('train.enc')
        filenames.append('train.dec')
    else:
        filenames.append('test.enc')
        filenames.append('test.dec')
    files = []
    for filename in filenames:
        files.append(open(os.path.join(PROCESSED_PATH, filename), 'w'))

    for i in range(len(sentences)):
        sentence = sentences[i]
        sentence = sentence.strip()
        category = categories[i]
        category = category.strip()
        if not (sentence == '' or category == ''):
            files[0].write(sentence + '\n')
            files[1].write(category + '\n')

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

    sentences, categories = sentence_categories(CORPUS_FILE)
    prepare_dataset(True, sentences, categories)
    sentences, categories = sentence_categories(TEST_FILE)
    prepare_dataset(False, sentences, categories)


def prepare_removed_words():
    # 准备停用词表
    words_to_be_removed_path = os.path.join(DATA_PATH, 'words_to_be_removed.txt')
    with open(words_to_be_removed_path, 'r', errors='ignore') as f:
        for word in f:
            if word:
                word = word.strip()
                words_to_be_removed.append(word)
                print('word=', word)


if __name__ == '__main__':
    prepare_removed_words()
    prepare_raw_data()
    process_data()
