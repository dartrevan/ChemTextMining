import nltk
from gensim.models import word2vec
import codecs
from spell_checker.spell_checker import correct


dict_adr_lex_location = 'vocabularies/adr_lexicon.txt'
dict_do_location = 'vocabularies/dict_do.txt'
dict_finding_location = 'vocabularies/dict_finding.txt'
dict_patterns_location = 'vocabularies/dict_patterns.txt'
dict_umls_location = 'vocabularies/dict_umls.txt'
dict_wiki_location = 'vocabularies/dict_wiki.txt'
dict_webmd_conditions_location = 'vocabularies/webmd_conditions.txt'
brown_clusters = {}
w2v_clusters = {}
w2vmodel = None

def load_w2v_model():
    global w2vmodel
    w2vmodel = word2vec.Word2Vec.load_word2vec_format('word2vec/Health_2.5mreviews.s200.w10.n5.v15.cbow.bin', binary=True)

def prepare_brown_clusters():
    global brown_clusters
    with codecs.open('clustered_words/brown_clusters/brown_input-150/paths', encoding = 'utf-8') as f:
        clusters_tree = f.readlines()
    brown_clusters = {word:cluster for word, cluster in map(lambda x: (x.split('\t')[1], x.split('\t')[0]), clusters_tree)}

def prepare_w2v_clusters():
    global w2v_clusters
    with codecs.open('clustered_words/w2v_clusters/word_clusters.txt', encoding='utf-8') as in_file:
        w2v_clusters = {word:cluster for word, cluster in map(lambda line: (line.split(' ')[0], int(line.split(' ')[1])), in_file.readlines())}


def word2vec_features(extended_token, key):
    w2v_features = {}
    if extended_token['token'] in w2vmodel:
        for i, num in enumerate(w2vmodel[extended_token['token']]):
            w2v_features['%s_%i' % (key, i)] = num
    return w2v_features

def suffix(extended_token, key):
    suffixes = {}
    suff_len = 2
    while suff_len <= 6 and len(extended_token['token']) > suff_len:
        suffixes['%s_suff_len%i' % (key, suff_len)] = extended_token['token'][-suff_len:].lower()
        suff_len += 1
    return suffixes


def prefix(extended_token, key):
    prefixes = {}
    pref_len = 2
    while pref_len <= 6 and len(extended_token['token']) > pref_len:
        prefixes['%s_pref_len%i' % (key, pref_len)] = extended_token['token'][:pref_len].lower()
        pref_len += 1
    return prefixes



def pos_tag(extended_token, key):
    return {key:extended_token['pos_tag']}


def lower_token(extended_token, key):
    return {key:extended_token['lemm']}

def isupper_token(extended_token, key):
    return {key:extended_token['token'].isupper()}

def istitle_token(extended_token, key):
    return {key:extended_token['token'].istitle()}

def brown_cluster_info(extended_token, key):
    token = correct(extended_token['token'].lower())
    return {key:brown_clusters[token]} if token in brown_clusters else dict()

def w2v_cluster_info(extended_token, key):
    token = extended_token['token'].lower()
    return {key:w2v_clusters[token] if token in w2v_clusters else -1}

def bias(extended_token, key):
    return {key:1.0}

def isin_adr(extended_token, key):
    return {key + 'B': extended_token['bio_%s' % dict_adr_lex_location] == 'B',
            key + 'I': extended_token['bio_%s' % dict_adr_lex_location] == 'I',
            key + 'O': extended_token['bio_%s' % dict_adr_lex_location] == 'O'
            }

def isin_do(extended_token, key):
    return {key + 'B': extended_token['bio_%s' % dict_do_location] == 'B',
            key + 'I': extended_token['bio_%s' % dict_do_location] == 'I',
            key + 'O': extended_token['bio_%s' % dict_do_location] == 'O'
            }

def isin_finding(extended_token, key):
    return {key + 'B': extended_token['bio_%s' % dict_finding_location] == 'B',
            key + 'I': extended_token['bio_%s' % dict_finding_location] == 'I',
            key + 'O': extended_token['bio_%s' % dict_finding_location] == 'O'
            }

def isin_patterns(extended_token, key):
    return {key+'B': extended_token['bio_%s' % dict_patterns_location] == 'B',
            key+'I': extended_token['bio_%s' % dict_patterns_location] == 'I',
            key + 'O': extended_token['bio_%s' % dict_patterns_location] == 'O'
            }

def isin_umls(extended_token, key):
    return {key + 'B': extended_token['bio_%s' % (dict_umls_location)] == 'B',
            key + 'I': extended_token['bio_%s' % (dict_umls_location)] == 'I',
            key + 'O': extended_token['bio_%s' % (dict_umls_location)] == 'O'
            }

def isin_wiki(extended_token, key):
    return {key + 'B': extended_token['bio_%s' % (dict_wiki_location)] == 'B',
            key + 'I': extended_token['bio_%s' % (dict_wiki_location)] == 'I',
            key + 'O': extended_token['bio_%s' % (dict_wiki_location)] == 'O'
            }

def isin_webmd(extended_token, key):
    return {key + 'B': extended_token['bio_%s' % (dict_webmd_conditions_location)] == 'B',
            key + 'I': extended_token['bio_%s' % (dict_webmd_conditions_location)] == 'I',
            key + 'O': extended_token['bio_%s' % (dict_webmd_conditions_location)] == 'O'

}

baseline_feature = {
    'lower': lower_token,
}

shape_features = {
    'isupper': isupper_token,
    'istitle': istitle_token,
}

suffixes_preffixes_features = {
    'prefix': prefix,
    'suffix':suffix,
}

pos_tag_feature = {
    'pos_tags': pos_tag
}

brown_cluster_feature = {
    'brown_cluster': brown_cluster_info
}

w2v_cluster_feature = {
    'w2v_cluster':w2v_cluster_info
}

dictionary_features = {
    'isin_adr_lex':isin_adr,
    #'isin_do':isin_do,
    #'isin_finding':isin_finding,
    'isin_patterns':isin_patterns,
    'isin_umls':isin_umls,
    #'isin_webmd':isin_webmd,
    #'isin_wiki':isin_wiki
}

bias_feature = {
    'bias': bias
}
w2v_features = {
    'w2v_features': word2vec_features
}

feature_types = {
    'baseline_feature':baseline_feature,
    'suffixes_preffixes_features':suffixes_preffixes_features,
    'bias_feature':bias_feature,
    'shape_features':shape_features,
    'pos_tag_feature':pos_tag_feature,
    'brown_cluster_feature':brown_cluster_feature,
    'dictionary_features':dictionary_features,
    'w2v_features':w2v_features,
    'w2v_cluster_feature':w2v_cluster_feature
}
