import string
import re
import codecs



class Dictionary(object):

    def clean_word(self, string):
        return string[:-1].lower()


    def init_letter_position(self, letter, search_start_position):
        pos = self.find_pos_in_vocabulary(letter, search_start_position, len(self.vocabulary))
        if pos is not None:
            self.positions[letter] = pos
        return pos or search_start_position


    def __init__(self, entity_name, dictionary_location):
        """
        initialize with dictionary
        """
        self.entity_name = entity_name
        with codecs.open(dictionary_location, encoding='utf-8') as in_file:
            self.vocabulary = map(self.clean_word, in_file.readlines())
        self.vocabulary = sorted(self.vocabulary)
        self.positions = {}
        search_start_position = 0
        for letter in string.ascii_lowercase:
            if self.vocabulary[-1][0] < letter:
                break
            search_start_position = self.init_letter_position(letter, search_start_position)

        for additional_symbol in ["'", '(']:
            self.init_letter_position(additional_symbol, 0)

    def __str__(self):
        return self.entity_name

    def find_pos_in_vocabulary(self, searching_line, start_index, stop_index):
        if stop_index >= start_index and start_index < len(self.vocabulary):
            middle = (start_index + stop_index)//2
            if self.vocabulary[middle][:len(searching_line)] >= searching_line:
                res = self.find_pos_in_vocabulary(searching_line, start_index, middle - 1)
                if res is not None:
                    return res
                elif self.vocabulary[middle][:len(searching_line)] == searching_line:
                    return middle
                else:
                    return None
            else:
                return self.find_pos_in_vocabulary(searching_line, middle + 1, stop_index)
        else:
            return None

    def find(self, searching_string, start_position=None):
        if ord(unicode(searching_string[0])) > 128:
            return (None, None)
        st_index = start_position or self.positions.get(searching_string[0], 0)
        #i = 0
        #while not self.positions.get(chr(ord(searching_string[0]) + 1), None) and i < 27:
            #i += 1
        sp_index = self.positions.get(chr(ord(searching_string[0]) + 1), len(self.vocabulary))
        index = self.find_pos_in_vocabulary(searching_string, st_index, sp_index)
        return (self.vocabulary[index], index) if index is not None else (None, None)

if __name__ == '__main__':
    e = Entity('entity_name', 'test_vocab.txt')
    for key, value in e.positions.items():
        if value is not None:
            print key, e.vocabulary[value]

    print e.find('(dummy text')
