import os
import re

class ann_files_iterator(object):


    def split_to_txt_ann_files(self, all_files):
        find_txt_files = lambda file_name: re.findall(r'.txt$', file_name)
        txt_to_ann_file_name = lambda file_name: re.sub(r'.txt$', '.ann', file_name)
        txt_files = filter(find_txt_files, all_files)
        ann_files = map(txt_to_ann_file_name, txt_files)
        return txt_files, ann_files

    def __init__(self, directory):
        self.directory = directory
        all_files = []
        for root, dirs, files in os.walk(directory):
            all_files += map(lambda file_: os.path.join(root, file_), files)
        self.txt_files, self.ann_files = self.split_to_txt_ann_files(all_files)



    def __iter__(self):
        return iter(zip(self.txt_files, self.ann_files))



if __name__ == '__main__':
    for txt_file, ann_file in ann_files_iterator('../annotated_data/'):
        assert re.sub(r'.txt$', '', txt_file) == re.sub(r'.ann$', '', ann_file)
        assert os.path.isfile(txt_file)
        assert os.path.isfile(ann_file)
