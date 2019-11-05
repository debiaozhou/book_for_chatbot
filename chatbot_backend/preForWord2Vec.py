folder = 'XXXXXX'


def segment(input, output):
    # 打开输入输出文件
    input_file = open(input, "r")
    output_file = open(output, "w")
    # 分词处理
    while True:
        # 读入输入文件的一行
        line = input_file.readline()
        if line:
            # 删除标识符
            new_line = ''
            if line[:4] == '- - ':
                new_line = line[4:]
            elif line[:2] == '- ':
                new_line = line[2:]
            output_file.write(new_line)
        else:
            break
    # 关闭文件
    input_file.close()
    output_file.close()


if __name__ == '__main__':
    #segment(sys.argv[1], sys.argv[2])
    segment(folder + "corpus.txt", folder + "corpusForWord2Vec.txt")