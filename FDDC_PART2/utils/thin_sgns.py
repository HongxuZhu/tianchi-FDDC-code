root = '/home/utopia/PycharmProjects/csahsaohdoashdoasdhoa/FDDC_PART2/expand/NER_IDCNN_CRF/data/'
in_file = root + 'sgns.merge.word'
out_file = open(root + 'sgns.merge.char', 'a+')


def thin():
    with open(in_file, 'r') as file:
        for line in file:
            line = line[0:len(line) - 2]
            array = line.split(' ')
            first = array[0]
            if len(first) == 1:
                out_file.write(line + '\n')


thin()
