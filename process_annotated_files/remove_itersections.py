import codecs
import json

input_file = '../corpus_json/corpus.txt'
output_file = '../corpus_json/corpus.txt'

def scope_cmp(entity_key_a, entity_key_b, entities):
    if entities[entity_key_a]['start'] < entities[entity_key_b]['start']:
        return -1
    elif entities[entity_key_a]['start'] == entities[entity_key_b]['start'] and entities[entity_key_a]['end'] >= entities[entity_key_b]['end']:
        return -1
    else:
        return 1


def remove_intersections_from_entities(review):
    entity_cmp = lambda key_a, key_b: scope_cmp(key_a, key_b, review['entities'])
    view_order =  sorted(review['entities'], cmp=entity_cmp)
    for i, current_element in enumerate(view_order):
        if current_element not in review['entities']:
            continue
        possibly_removing_entities = view_order[i+1:]
        for element_for_check in possibly_removing_entities:
            if review['entities'][current_element]['end'] < review['entities'][element_for_check]['start']:
                break
            if review['entities'][element_for_check]['entity'] == review['entities'][current_element]['entity']:
                del review['entities'][element_for_check]

        if review['entities'][current_element]['entity'] != 'Disease':
            del review['entities'][current_element]

if __name__ == '__main__':
    with codecs.open(input_file, encoding='utf-8') as in_file:
        reviews = map(json.loads, in_file.readlines())

    """
    sort all entities by offsets
    """
    for review in reviews:
        remove_intersections_from_entities(review)

    with codecs.open(output_file, 'w', encoding='utf-8') as out_file:
        for review in reviews:
            out_file.write(json.dumps(review) + u'\n')
