import logging
import gensim
from gensim.models import word2vec
from sklearn.decomposition import PCA
from matplotlib import pyplot


folder = 'XXXXXX'
pyplot.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
pyplot.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def vector(input, output):
    # 设置输出日志
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    # 读取分词好的文件
    sentences = word2vec.LineSentence(input)
    # 训练模型
    model = gensim.models.Word2Vec(sentences, size=200, min_count=5)
    # 保存
    model.wv.save_word2vec_format(output, binary=True)
    print(model)
    print(model['语言'])
    # 图像化表示
    X = model[model.wv.vocab]
    pca = PCA(n_components=2)
    result = pca.fit_transform(X)
    pyplot.scatter(result[:, 0], result[:, 1])
    words = list(model.wv.vocab)
    for i, word in enumerate(words):
        pyplot.annotate(word, xy=(result[i, 0], result[i, 1]))
    pyplot.show()


if __name__ == '__main__':
    #word2vec(sys.argv[1], sys.argv[2])
    vector(folder + "corpusForWord2Vec.txt", folder + "embedding.bin")
