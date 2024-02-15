import sys
import math
import tflearn
import tensorflow as tf
import numpy as np
import os
from gensim.models import KeyedVectors
import jieba


folder = '/Users/debiao/Downloads/Test/open_domain/'
embedding = 'embedding.bin'
max_sentence_length = 16
word_vector_dim = 200
word_vector_dict = {}
train_encode = '/Users/debiao/Documents/Project/Book/open_domain/train.enc'
train_decode = '/Users/debiao/Documents/Project/Book/open_domain/train.dec'
test_encode = '/Users/debiao/Documents/Project/Book/open_domain/test.enc'
test_decode = '/Users/debiao/Documents/Project/Book/open_domain/test.dec'
test_questions = '/Users/debiao/Downloads/Test/open_domain/testQuestions.txt'


def load_data(file_name):
    # 加载数据

    scripts = []
    with open(file_name, 'r', errors='ignore') as f:
        for line in f:
            if line:
                scripts.append(line.strip())
                print('line=', line.strip())
    return scripts


def load_vector():
    # 加载词向量，key：词；value：200维的向量

    print('开始加载词向量')
    file_path = os.path.join(folder, embedding)
    model = KeyedVectors.load_word2vec_format(file_path, binary=True)
    words = list(model.wv.vocab)
    print('words=', words)
    for word in words:
        print(word)
        word_vector_dict[word] = model[word]
        print(model[word])
    print('加载词向量结束')


def init_data(input_file):
    # 读取训练数据以及测试数据，加载词向量

    scripts_embedding = []
    scripts = load_data(input_file)
    for index in range(len(scripts)):
        words = []
        script = scripts[index]
        for word in script.split(' '):
            if word_vector_dict.__contains__(word):
                words.append(word_vector_dict[word])
            else:
                print('not in dict word=', word)
        scripts_embedding.append(words)
    return scripts_embedding


def get_data(questions, answers):
    # 准备输入输出数据

    xy_data = []
    y_data = []
    for i in range(len(questions)):
        question = questions[i]
        answer = answers[i]
        if 0 < len(question) < max_sentence_length and 0 < len(answer) < max_sentence_length:
            sequence_xy = [np.zeros(word_vector_dim)] * (max_sentence_length - len(question)) + list(
                reversed(question))
            sequence_y = answer + [np.zeros(word_vector_dim)] * (max_sentence_length - len(answer))
            sequence_xy = sequence_xy + sequence_y
            sequence_y = [np.ones(word_vector_dim)] + sequence_y
            xy_data.append(sequence_xy)
            y_data.append(sequence_y)
        else:
            print('exceeded mqx_seq_len question=', len(question))
            print('exceeded mqx_seq_len answer=', len(answer))

    return np.array(xy_data), np.array(y_data)


def get_test_data(questions):
    # 准备测试数据

    xy_data = []
    for i in range(len(questions)):
        question = questions[i]
        if 0 < len(question) < max_sentence_length:
            sequence_xy = [np.zeros(word_vector_dim)] * (max_sentence_length - len(question)) + list(
                reversed(question))
            sequence_y = [np.zeros(word_vector_dim)] * max_sentence_length
            sequence_xy = sequence_xy + sequence_y
            xy_data.append(sequence_xy)
        else:
            print('exceeded mqx_seq_len question=', len(question))

    return np.array(xy_data)


def vector_sqrtlen(vector):
    len = 0
    for item in vector:
        len += item * item
    len = math.sqrt(len)
    return len


def vector_cosine(v1, v2):
    if len(v1) != len(v2):
        sys.exit(1)
    sqrtlen1 = vector_sqrtlen(v1)
    sqrtlen2 = vector_sqrtlen(v2)
    value = 0
    for item1, item2 in zip(v1, v2):
        value += item1 * item2
    return value / (sqrtlen1*sqrtlen2)


def vector2word(vector):
    max_cos = -10000
    match_word = ''
    for word in word_vector_dict:
        v = word_vector_dict[word]
        cosine = vector_cosine(vector, v)
        if cosine > max_cos:
            max_cos = cosine
            match_word = word
    return (match_word, max_cos)


class Chatbot_Model(object):
    def __init__(self):
        # 初始化

        self.max_sentence_length = max_sentence_length
        self.word_vector_dim = word_vector_dim

    def prepare_data(self):
        # 准备数据

        load_vector()
        trainX, trainY = get_data(init_data(train_encode), init_data(train_decode))
        testX, testY = get_data(init_data(test_encode), init_data(test_decode))

        return np.array(trainX), np.array(trainY), np.array(testX), np.array(testY)

    def model(self, feed_previous=False):
        # 建立模型

        input_data = tflearn.input_data(shape=[None, self.max_sentence_length * 2, self.word_vector_dim], dtype=tf.float32, name="xy")
        encoder_inputs = tf.slice(input_data, [0, 0, 0], [-1, self.max_sentence_length, self.word_vector_dim], name="enc_in")
        (encoder_output_tensor, states) = tflearn.lstm(encoder_inputs, self.word_vector_dim, return_state=True, scope='enc_lstm')
        encoder_output_sequence = tf.stack([encoder_output_tensor], axis=1)

        decoder_inputs_tmp = tf.slice(input_data, [0, self.max_sentence_length, 0], [-1, self.max_sentence_length-1, self.word_vector_dim], name="dec_in_tmp")
        go_inputs = tf.slice(tf.ones_like(decoder_inputs_tmp), [0, 0, 0], [-1, 1, self.word_vector_dim])
        decoder_inputs = tf.concat([go_inputs, decoder_inputs_tmp], 1, name="dec_in")

        if feed_previous:
            first_dec_input = go_inputs
        else:
            first_dec_input = tf.slice(decoder_inputs, [0, 0, 0], [-1, 1, self.word_vector_dim])
        decoder_output_tensor = tflearn.lstm(first_dec_input, self.word_vector_dim, initial_state=states, return_seq=False, reuse=False, scope='decoder_lstm')
        decoder_output_sequence_single = tf.stack([decoder_output_tensor], axis=1)
        decoder_output_sequence_list = [decoder_output_tensor]

        for i in range(self.max_sentence_length-1):
            if feed_previous:
                next_dec_input = decoder_output_sequence_single
            else:
                next_dec_input = tf.slice(decoder_inputs, [0, i+1, 0], [-1, 1, self.word_vector_dim])
            decoder_output_tensor = tflearn.lstm(next_dec_input, self.word_vector_dim, return_seq=False, reuse=True, scope='decoder_lstm')
            decoder_output_sequence_single = tf.stack([decoder_output_tensor], axis=1)
            decoder_output_sequence_list.append(decoder_output_tensor)

        decoder_output_sequence = tf.stack(decoder_output_sequence_list, axis=1)
        real_output_sequence = tf.concat([encoder_output_sequence, decoder_output_sequence], 1)

        net = tflearn.regression(real_output_sequence, optimizer='sgd', learning_rate=0.1, loss='mean_square')
        model = tflearn.DNN(net, tensorboard_verbose=3, tensorboard_dir='tflearn_logs')
        return model

    def train(self):
        # 训练模型

        trainX, trainY, testX, testY = self.prepare_data()
        model = self.model(feed_previous=False)
        model.fit(trainX, trainY, validation_set=(testX, testY), n_epoch=1000, show_metric=True, batch_size=2)
        model.save('model.tflearn201905')
        return model

    def load(self):
        model = self.model(feed_previous=True)
        model.load('model.tflearn201905')
        return model

    def predict(self, question):
        model = self.load()
        testX = prepare_test_data_from_input(question)
        predict = model.predict(testX)
        answer = ''
        for sample in predict:
            print('预测回答')
            for w in sample[1:]:
                (match_word, max_cos) = vector2word(w)
                print(match_word, max_cos, vector_sqrtlen(w))
                answer = answer + match_word
        return answer


def prepare_test_data():
    # 准备数据

    load_vector()
    testX = get_test_data(init_data(test_questions))
    #testX = get_test_data(init_data(test_encode))

    return np.array(testX)


def prepare_test_data_from_input(question):
    # 准备数据

    load_vector()
    # 结巴分词
    segment_list = jieba.cut(question)
    # 输出分词结果
    segments = ""
    for segment in segment_list:
        if segments == "":
            segments = segment
        else:
            segments = segments + " " + segment
    print('input=', segments)
    # 转换词向量
    scripts_embedding = []
    words = []
    for word in segments.split(' '):
        if word_vector_dict.__contains__(word):
            words.append(word_vector_dict[word])
        else:
            print('not in dict word=', word)
        scripts_embedding.append(words)
    # 准备模型的输入输出数据
    testX = get_test_data(scripts_embedding)
    return np.array(testX)


def predict(self, question):
    model = self.load()
    testX = prepare_test_data_from_input(question)
    predict = model.predict(testX)
    answer = ''
    for sample in predict:
        print('')
        for w in sample[1:]:
            (match_word, max_cos) = vector2word(w)
            print(match_word, max_cos, vector_sqrtlen(w))
            answer = answer + match_word
    return answer


if __name__ == '__main__':
    phrase = 'train'
    my_seq2seq = Chatbot_Model()
    if phrase == 'train':
        my_seq2seq.train()
    elif phrase == 'test':
        model = my_seq2seq.load()
        testX = prepare_test_data()
        predict = model.predict(testX)
        for sample in predict:
            print('预测回答')
            index = 0
            for w in sample[1:]:
                (match_word, max_cos) = vector2word(w)
                print(match_word, max_cos, vector_sqrtlen(w))
                if index < 9:
                    index = index + 1
