import os
from crf.compose_dataset import compose_dataset
from numpy.random import choice


class Fold(object):

    def __init__(self, fold_train_conll_location, fold_test_conll_location, features, in_memory=True):
        self.features = features
        self.fold_test_conll_location = fold_test_conll_location
        self.fold_train_conll_location = fold_train_conll_location
        if in_memory:
            self.train = compose_dataset(fold_train_conll_location, features)
            self.test = compose_dataset(fold_test_conll_location, features)

    def __getitem__(self, index):
        if index == 'test':
            return self.test if hasattr(self, 'test') else compose_dataset(self.fold_test_conll_location, self.features)
        elif index == 'train':
            return self.train if hasattr(self, 'train') else compose_dataset(self.fold_train_conll_location, self.features)
        else:
            raise KeyError(index)
