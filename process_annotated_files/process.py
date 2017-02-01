# -*- coding: utf-8 -*-
import re
from ann_files_iterator import ann_files_iterator
import codecs
from parse import parse
import json
import os
from remove_itersections import remove_intersections_from_entities, remove_intersections
from correct_text import correct_review

ann_data_directory = '../annotated_data'
output_directory = '../corpus_json'
output_filename = 'corpus.txt'

class EntityNotInText(Exception):
    pass

def parse_txt_file(txt_file):
    with codecs.open(txt_file, encoding='utf-8') as in_file:
        content = in_file.readlines()

    content = map(lambda line: line.strip('\n'), content)
    id_ = int(content[0].split(':')[1])
    url = content[1].split(':')[1]
    title = content[3]
    text = content[5]
    rating = int(content[6].split(':')[1])
    condition = content[7].split(':')[1]
    back = len(''.join(content[:5])) + 4

    return id_, url, title, text, rating, condition, back

def parse_txt_file_med_reviews(txt_file):
    with codecs.open(txt_file, encoding='utf-8') as in_file:
        content = in_file.readlines()

    id_ = os.path.basename(txt_file).split('.')[0]
    content = map(lambda line: line.strip('\n'), content)
    url = content[0]
    title = content[2]
    text = content[4]
    rating = int(content[6])
    back = len(''.join(content[:4])) + 3

    return id_, url, title, text, rating, back

def is_entity(line):
    return re.findall(r'^T[0-9]+', line)

def is_type(line):
    return re.findall(r'^A[0-9]+', line)


def parse_start_end(positions, review_text, annotation_text, back):
    starts = []
    ends = []
    parse_pair_string = '{:d} {:d}'
    for start_end_str in re.findall(r'[0-9]+ [0-9]+', positions):
        start, end = parse(parse_pair_string, start_end_str).fixed
        #print start, end
        start, end = start - back, end - back
        if len(review_text) >= end - 1  and start >= -1:
            step = 0
            if review_text[start + 1:end + 1] == annotation_text[:end-start]:
                step = 1
            elif review_text[start - 1:end - 1] == annotation_text[:end-start]:
                step = -1
            start, end = start + step, end + step
            assert review_text[start:end] == annotation_text[:end-start], ' Expected |%s|, Actual |%s|' % (annotation_text, review_text[start:end])
            removing_str = re.sub('\(','\(', review_text[start:end])
            removing_str = re.sub('\)','\)', removing_str)
            annotation_text = re.sub('^%s[ ]*' % removing_str, '', annotation_text)
            starts += [start]
            ends += [end]
        else:
            raise EntityNotInText('Entity not in text scope')

    start = min(starts)
    end = max(ends)
    return start, end, review_text[start:end]


def parse_ann_file(ann_file, review_text, back):
    entities = {}
    with codecs.open(ann_file, encoding='utf-8') as in_file:
        content = in_file.readlines()

    content = map(lambda line: line.strip('\n'), content)
    entity_parse_string = '{entity_id}\t{entity} {positions}\t{text}'
    type_parse_string = '{type_id}\t{type_name} {entity_id} {type}'
    for line in content:
        if is_entity(line):
            try:
                entity = parse(entity_parse_string, line).named
                positions = entity['positions']
                start, end, text = parse_start_end(positions, review_text, entity['text'], back)
                entities[entity['entity_id']] = {}
                entities[entity['entity_id']]['entity'] = entity['entity']
                entities[entity['entity_id']]['start'] = start
                entities[entity['entity_id']]['end'] = end
                entities[entity['entity_id']]['text'] = text
            except EntityNotInText:
                pass
        elif is_type(line):
            type_ = parse(type_parse_string, line).named
            entity_id = type_['entity_id']
            entity_type = type_['type']
            type_name = type_['type_name']
            if entity_id in entities:
                if type_name != 'Sentiment':
                    entities[entity_id]['type'] = entity_type
                else:
                    entities[entity_id]['sentiment'] = entity_type

    return entities

def process_annotated_data(output_directory, input_directory):
    with codecs.open(os.path.join(output_directory, output_filename), 'w', encoding='utf-8') as out_file:
        for txt_file, ann_file in ann_files_iterator(input_directory):
            review = {}
            id_, url, title, text, rating, condition, back = parse_txt_file(txt_file)
            #print id_
            entities = parse_ann_file(ann_file, text, back)
            if entities:
                review['id'] = id_
                review['url'] = url
                review['title'] = title
                review['text'] = text
                review['rating'] = rating
                review['condition'] = condition
                review['entities'] = entities
                remove_intersections_from_entities(review)
                remove_intersections_(review)
                correct_review(review)
                out_file.write(json.dumps(review) + u'\n')


def process_annotated_data_med_reviews(output_directory, input_directory):
    with codecs.open(os.path.join(output_directory, output_filename), 'w', encoding='utf-8') as out_file:
        for txt_file, ann_file in ann_files_iterator(input_directory):
            review = {}
            id_, url, title, text, rating, back = parse_txt_file_med_reviews(txt_file)
            entities = parse_ann_file(ann_file, text, back)
            if entities:
                review['id'] = id_
                review['url'] = url
                review['title'] = title
                review['text'] = text
                review['rating'] = rating
                review['entities'] = entities
                remove_intersections_from_entities(review)
                #correct_review(review)
                out_file.write(json.dumps(review, ensure_ascii=False) + u'\n')

if __name__ == '__main__':
    process_annotated_data(output_directory, ann_data_directory)
