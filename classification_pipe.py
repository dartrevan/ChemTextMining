from process_annotated_files.json_to_conll import json_to_conll
from folds import Fold
from crf.postprocessing import save_pred_conll, save_pred_json
import sklearn_crfsuite
from os import popen, path
from numpy import mean, arange
import numpy as np




"""
    Available features:

    baseline_feature
    suffixes_preffixes_features
    bias_feature
    shape_features
    pos_tag_feature
    brown_cluster_feature
    dictionary_features
    w2v_features
    w2v_cluster_feature
"""

update_conll_folds = False # set to true if json folds are updated
folds_locations = ['corpus_json/%i/' % i for i in range(5)] # location of folds
in_memory = True # persist all folds in memory

features = {
    'current_features':['baseline_feature'],
    'prev_features':[],
    'next_features':[],
    'k_prev':0,
    'k_next':0
}


def exact_eval(output_file_loc):
    exact_lines = popen('evaluation/./conlleval < %s' % output_file_loc).readlines()
    exact_fscore = exact_lines[1].split(';')[3].split(':')[1]
    exact_precision = exact_lines[1].split(';')[1].split(':')[1].strip('%')
    exact_recall = exact_lines[1].split(';')[2].split(':')[1].strip('%')

    return exact_precision, exact_recall, exact_fscore

def weak_eval(gold_file, pred_file):
    weak_lines = popen('python evaluation/eval.py -g %s -t %s -w weak' % (gold_file, pred_file)).readlines()
    weak_fscore = weak_lines[-1].split('\t')[3]
    weak_precision = weak_lines[-1].split('\t')[1]
    weak_recall = weak_lines[-1].split('\t')[2]

    return weak_precision, weak_recall, weak_fscore


if __name__ == '__main__':
    if update_conll_folds:
        for fold_location in folds_locations:
            json_to_conll(fold_location + 'train/train.json', fold_location + 'train/conll_train.txt')
            json_to_conll(fold_location + 'test/test.json', fold_location + 'test/conll_test.txt')
    folds = [Fold(path.join(fold_location + 'train/conll_train.txt'), path.join(fold_location + 'test/conll_test.txt'), features, in_memory=in_memory) for fold_location in folds_locations]

    params_space = [
                    {'algorithm':'pa', 'pa_type':0},
                    {'algorithm':'pa', 'pa_type':1},
                    {'algorithm':'pa', 'pa_type':2}
                ]
    crf = sklearn_crfsuite.CRF(
                            max_iterations=100,
                            all_possible_transitions=True,
                        )
    fold_exact_scores = []
    fold_weak_scores = []

    for i, fold in enumerate(folds):
        conll_pred_output_location = 'corpus_json/corpus_conll_pred_%i.txt'
        y_train, X_train, tokens_train, positions, spaces, ids = fold['train']
        y_test, X_test, tokens_test, positions_test, spaces_test, ids_test = fold['test']

        exact_scores = []
        weak_scores = []

        for params in params_space:
            print 'Training on %i fold with params' % i, params

            crf.set_params(**params)
            crf.fit(X_train, y_train)
            y_pred = crf.predict(X_test)

            save_pred_json(y_pred, tokens_test, positions_test, spaces_test, ids_test, folds_locations[i] + 'test/test.json', 'corpus_json/corpus_pred_%i.txt' % i)
            save_pred_conll(conll_pred_output_location, y_test, y_pred, tokens_test)

            exact_score = exact_eval(conll_pred_output_location)
            weak_score = weak_eval('corpus_json/corpus_pred_%i.txt' % i, 'corpus_json/corpus_pred_%i.txt' % i)

            exact_score = map(float, exact_score)
            weak_score = map(float, weak_score)
            exact_scores += [exact_score]
            weak_scores += [weak_score]

            print weak_score
            print exact_score

        fold_exact_scores += [max(exact_scores, key=lambda x: x[2])]
        fold_weak_scores += [max(weak_scores, key=lambda x: x[2])]


    fold_exact_scores = np.array(fold_exact_scores)
    fold_weak_scores = np.array(fold_weak_scores)

    print u'Average exact score:\n{:0.4f}\t{:0.4f}\t{:0.4f}'.format(mean(fold_exact_scores[:, 0])/100, mean(fold_exact_scores[:, 1])/100, mean(fold_exact_scores[:, 2])/100)
    print u'Average weak score:\n{:0.4f}\t{:0.4f}\t{:0.4f}'.format(mean(fold_weak_scores[:, 0]), mean(fold_weak_scores[:, 1]), mean(fold_weak_scores[:, 2]))

