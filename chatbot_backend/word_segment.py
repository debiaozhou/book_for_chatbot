import jieba
import os


folder = 'XXXXXX'
max_sentence_length = 16


def segment(input, output):
    # 中文自动分词

    # 准备停用词表
    words_to_be_removed = []
    words_to_be_removed_path = os.path.join(folder, 'words_to_be_removed.txt')
    with open(words_to_be_removed_path, 'r', errors='ignore') as f:
        for word in f:
            if word:
                word = word.strip()
                words_to_be_removed.append(word)
                print('word=', word)
    # 打开输入输出文件
    input_file = open(input, "r")
    output_file = open(output, "w")
    # 分词处理
    while True:
        # 读入输入文件的一行
        line = input_file.readline()
        if line:
            # 结巴分词
            segment_list = jieba.cut(line)
            # 输出分词结果
            segments = ""
            index = 0
            for segment in segment_list:
                # 删除停用词
                segment = segment.strip()
                if segment not in words_to_be_removed:
                    if segments == "":
                        segments = segment
                        index = index + 1
                    else:
                        if index < max_sentence_length:
                            segments = segments + " " + segment
                            index = index + 1
                        else:
                            if len(segments) >= 1:
                                output_file.write(segments + "\n")
                            segments = "- " + segment
                            index = 0
            if len(segments) >= 1:
                output_file.write(segments + "\n")
        else:
            break
    # 关闭文件
    input_file.close()
    output_file.close()


if __name__ == '__main__':
    #segment(sys.argv[1], sys.argv[2])
    segment(folder + "corpus_origin_with_category.txt", folder + "corpus.txt")