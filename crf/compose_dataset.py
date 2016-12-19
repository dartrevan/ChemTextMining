from joblib import Parallel, delayed
import string
from nltk.stem import WordNetLemmatizer
from features import *
from corpus_json.conll_iterator import conll_sentences
from vocabularies.dictionary import Dictionary


dictionaries = {}



def prepare_dictionary(dic_location):
    if dic_location not in dictionaries:
        print "Preparing %s dictionary" % dic_location.split('/')[-1]
        dictionaries[dic_location] = Dictionary('name', dic_location)
        print 'Done'

def parse_line(line):
    token, lemm, pos_tag, bio_tag, w_start, w_end, delimitter, id_ = line.split('\t')
    return {
            'token':token,
            'lemm':lemm,
            'pos_tag':pos_tag,
            'bio_tag':bio_tag,
            'w_start':w_start,
            'w_end':w_end,
            'delimitter':delimitter,
            'id':id_
        }

def parse_sent(sent):
    return map(parse_line, sent)


def extract_features_for_token(extended_token, app = '', features = {}):
    token_features = {}
    for key, token_feature in features.iteritems():
        key_feature = token_feature(extended_token, key + app)
        if not isinstance(key_feature, dict):
            raise Exception("%s functions must return features dictionary, but returned %s" % (key, type(key_feature)))
        token_features.update(key_feature)
    return token_features

def add_prev_tokens(extended_tokens, i, k = 2, prev_token_features = {}, only_words = False):
    prev_tokens = {}
    step = 0
    while i > 0 and k>0:
        i -= 1
        step += 1
        prev_tokens.update(extract_features_for_token(extended_tokens[i], '_prev_%i' % step, prev_token_features))
        k -= 1
    return prev_tokens

def add_next_tokens(extended_tokens, i, k = 2, next_token_features = {}, only_words = False):
    next_tokens = {}
    step = 0
    while i < len(extended_tokens) - 1 and k>0:
        i += 1
        step += 1
        next_tokens.update(extract_features_for_token(extended_tokens[i], '_next_%i' % step, next_token_features))
        k -= 1
    return next_tokens



def dictionary_bio_extend(extended_tokens, dictionary_location):
    dictionary = dictionaries[dictionary_location]
    token_ind = 0
    tokens_cnt = len(extended_tokens)
    while token_ind < tokens_cnt:
        pattern = ''
        prev_pattern = ''
        index = 0
        found_string = None
        token_ind_ = token_ind
        while token_ind_ < tokens_cnt:
            pattern += ('' if not pattern else extended_tokens[token_ind_]['delimitter']) + extended_tokens[token_ind_]['token'].lower()
            found_string_, index = dictionary.find(pattern, index)
            if not found_string_ and (found_string == prev_pattern or not found_string):
                break
            found_string = found_string_
            prev_pattern = pattern
            token_ind_ += 1
        if found_string == prev_pattern:
            extended_tokens[token_ind]['bio_%s' % (dictionary_location)] = 'B'
            for j in range(token_ind + 1, token_ind_):
                extended_tokens[j]['bio_%s' % (dictionary_location)] = 'I'
            token_ind = token_ind_
        else:
            extended_tokens[token_ind]['bio_%s' % (dictionary_location)] = 'O'
            token_ind += 1

    return extended_tokens


def word2features(extended_tokens, i, current_token_features, prev_tokens_features, next_tokens_features, k_prev, k_next):
    features = {}
    features.update(extract_features_for_token(extended_tokens[i], features=current_token_features))
    features.update(add_prev_tokens(extended_tokens, i, k_prev, prev_tokens_features))
    features.update(add_next_tokens(extended_tokens, i, k_next, next_tokens_features))
    #features.update({'BOS': i == 0, 'EOS': i == len(extended_tokens) - 1})
    return features


def sent2vectors(sent, prev_tokens_features = {}, next_tokens_features = {}, current_token_features = {}, k_prev = 1, k_next = 1, dicts = None):
    X = []
    Y = []
    tokens = []
    positions = []
    spaces = []
    ids = []

    extended_tokens = parse_sent(sent)
    if dicts:
        extended_tokens = dictionary_bio_extend(extended_tokens, dict_adr_lex_location)
        extended_tokens = dictionary_bio_extend(extended_tokens, dict_patterns_location)
        extended_tokens = dictionary_bio_extend(extended_tokens, dict_do_location)
        extended_tokens = dictionary_bio_extend(extended_tokens, dict_finding_location)
        extended_tokens = dictionary_bio_extend(extended_tokens, dict_umls_location)
        extended_tokens = dictionary_bio_extend(extended_tokens, dict_wiki_location)
        extended_tokens = dictionary_bio_extend(extended_tokens, dict_webmd_conditions_location)

    for i, extended_token in enumerate(extended_tokens):
        X += [word2features(extended_tokens, i, current_token_features, prev_tokens_features, next_tokens_features, k_prev, k_next)]
        Y += [extended_token['bio_tag']]
        tokens += [extended_token['token']]
        positions += [{'start':extended_token['w_start'], 'end':extended_token['w_end']}]
        spaces += [extended_token['delimitter']]
        ids += [extended_token['id']]

    return Y, X, tokens, positions, spaces, ids


def compose_dataset(conll_file_location, features):

    current_token_features = {}
    prev_tokens_features = {}
    next_tokens_features = {}
    dicts = False

    for feature in features['current_features']:
        current_token_features.update(feature_types[feature])

    for feature in features['prev_features']:
        prev_tokens_features.update(feature_types[feature])

    for feature in features['next_features']:
        next_tokens_features.update(feature_types[feature])

    if 'dictionary_features' in features['current_features'] or 'dictionary_features' in features['prev_features'] or 'dictionary_features' in features['next_features']:
        prepare_dictionary(dict_adr_lex_location)
        prepare_dictionary(dict_do_location)
        prepare_dictionary(dict_finding_location)
        prepare_dictionary(dict_patterns_location)
        prepare_dictionary(dict_umls_location)
        prepare_dictionary(dict_wiki_location)
        prepare_dictionary(dict_webmd_conditions_location)
        dicts = True

    if 'brown_cluster_feature' in features['current_features'] or 'brown_cluster_feature' in features['prev_features'] or 'brown_cluster_feature' in features['next_features']:
        prepare_brown_clusters()

    if 'w2v_cluster_feature' in features['current_features']:
        prepare_w2v_clusters()

    if 'w2v_features' in features['current_features'] or 'w2v_feature' in features['prev_features'] or 'w2v_feature' in features['next_features']:
        load_w2v_model()


    res = Parallel(n_jobs=4)(delayed(sent2vectors)(sent, prev_tokens_features=prev_tokens_features, next_tokens_features=next_tokens_features, current_token_features=current_token_features, k_prev=features['k_prev'], k_next=features['k_next'], dicts = dicts) for sent in conll_sentences(conll_file_location))
    Y, X, tokens, positions, spaces, ids = zip(*res)
    return Y, X, tokens, positions, spaces, ids
