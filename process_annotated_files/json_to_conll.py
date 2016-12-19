import codecs
import json
from nltk.tokenize import wordpunct_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import wordnet
from spell_checker.spell_checker import correct




tagger = nltk.data.load('taggers/maxent_treebank_pos_tagger/english.pickle')
lemmatizer = WordNetLemmatizer()

def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def get_bio_tag(w_start, w_end, entities):
    for key, entity in entities.iteritems():
        if not isinstance(entity['start'], int):
            raise Exception("Entitie start must be an integer")
        if 'end'not in entity or not isinstance(entity['end'], int):
            raise Exception("Entities end must be an integer")
        start = entity['start']
        end = entity['end']
        if w_start > start and w_end <= end:
            return 'I-' + 'DIS'
        elif w_start == start and w_end <= end:
            return 'B-' + 'DIS'
    return 'O'

def get_token_position_in_text(token, w_start, text):
    delimitter_start = None
    while text[w_start:w_start+len(token)] != token:
        w_start += 1
        delimitter_start = delimitter_start or w_start
    return w_start, w_start + len(token), text[delimitter_start:w_start]


def json_to_conll(corpus_json_location, output_location, by_sent = False):
    with codecs.open(corpus_json_location, encoding='utf-8') as in_file:
        reviews = map(json.loads, in_file.readlines())

    with codecs.open(output_location, 'w', encoding='utf-8') as out_file:
        for review in reviews:
            documents = sent_tokenize(review['text']) if by_sent else [review['text']]
            w_start = 0
            w_end = 0
            for document in documents:
                tokens = wordpunct_tokenize(document)
                corrected_tokens = map(correct, tokens)
                pos_tags = tagger.tag(corrected_tokens)
                for token, temp in zip(tokens, pos_tags):
                    token_corr = temp[0]
                    pos_tag = temp[1]
                    w_start, w_end, delimitter = get_token_position_in_text(token, w_start, review['text'])
                    bio_tag = get_bio_tag(w_start, w_end, review['entities'])
                    lemm = lemmatizer.lemmatize(token_corr, get_wordnet_pos(pos_tag))
                    out_file.write(u'{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(token, lemm, pos_tag, bio_tag, w_start, w_end, delimitter, review['id']))
                    w_start = w_end - 1
                out_file.write('\n')



if __name__ == '__main__':
    json_to_conll('../corpus_json/corpus_2.txt', by_sent = True)

