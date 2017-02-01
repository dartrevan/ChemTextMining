import codecs
import json
import re
from ChemTextMining.spell_checker.spell_checker import correct

tokenize = lambda string: re.split('(\W)', string)

def correct_text(text):
    tokens = tokenize(text)
    corrected_text = []
    for token in tokens:
        if token not in [' ', '.', '!']:
            is_upper = token.isupper()
            is_title = token.istitle()
            token = token.lower()
            token = correct(token)
            token = token.upper() if is_upper else token
            token = token.title() if is_title else token
        corrected_text += [token]
    return ''.join(corrected_text)


def correct_review(review):
    text = review['text']
    entities = review['entities']
    prev_entity_end = 0
    text_parts = []
    concat_parts = []
    for key, entity in sorted(entities.iteritems(), key=lambda e: e[1]['start']):
        start = entity['start']
        end = entity['end']
        text_part = text[prev_entity_end:start]
        text_parts += [{'text part':text_part, 'entity':None, 'start':prev_entity_end, 'end':start}]
        text_part = text[start:end]
        text_parts += [{'text part':text_part, 'entity':entity, 'start':start, 'end':end}]
        prev_entity_end = end

    text_part = text[prev_entity_end:]
    text_parts += [{'text part':text_part, 'entity':None, 'start':prev_entity_end, 'end':len(text)}]

    corrected_text = []
    offset_shift = 0
    current_end = 0
    for part in text_parts:
        corrected_part = correct_text(part['text part'])
        if current_end < part['end']:
            corrected_text += corrected_part
        if part['entity']:
            part['entity']['start'] += offset_shift
            part['entity']['end'] = part['entity']['start'] + len(corrected_part)
            part['entity']['text'] = corrected_part

        if current_end < part['end']:
            offset_shift += len(corrected_part) - len(part['text part'])
            current_end = part['end']

    review['text'] = ''.join(corrected_text)
