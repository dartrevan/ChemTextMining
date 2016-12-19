import codecs

class conll_sentences(object):

    def __init__(self, conll_file_location):
        with codecs.open(conll_file_location, encoding='utf-8') as in_file:
            self.conll_lines = in_file.readlines()


    def __iter__(self):
        self.cur_line = 0
        return self

    def next(self):
        if self.cur_line >= len(self.conll_lines):
            raise StopIteration
        lines = []
        while self.conll_lines[self.cur_line] != '\n':
            lines += [self.conll_lines[self.cur_line]]
            self.cur_line += 1
        self.cur_line += 1
        return map(lambda line: line.strip('\n'), lines)


if __name__ == '__main__':
    for sent in conll_sentences('corpus_conll_train.txt'):
        print sent
        input()
