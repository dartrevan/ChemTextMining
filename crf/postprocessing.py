import json
import codecs

def save_pred_conll(file_location, labels_true, labels_pred, tokens):
    with codecs.open(file_location, 'w', encoding='utf-8') as out_file:
        for review_labels_true, review_labels_pred, review_tokens in zip(labels_true, labels_pred, tokens):
            for label_true, label_pred, token in zip(review_labels_true, review_labels_pred, review_tokens):
                out_file.write(u'{} {} {}\n'.format(token, label_true, label_pred))
            out_file.write(u'\n')

def save_pred_json(labels, tokens, positions, spaces, ids, corpus_json_location, corpus_pred_output):
    with codecs.open(corpus_json_location, encoding='utf-8') as in_file:
        reviews = map(json.loads, in_file.readlines())
    for doc_labels, doc_tokens, doc_positions, doc_spaces, docs_ids in zip(labels, tokens, positions, spaces, ids):
        curr_id = int(docs_ids[0])
        curr_review = [review for review in reviews if review['id'] == curr_id][0]
        if 'entities_pred' not in curr_review:
            curr_review['entities_pred'] = {}
        entities_pred = curr_review['entities_pred']
        T = len(entities_pred)
        prev_label = ''
        for label, token, position, space, id_ in zip(doc_labels, doc_tokens, doc_positions, doc_spaces, docs_ids):
            if prev_label in ['O', ''] and label in ['B-DIS', 'I-DIS'] or label == 'B-DIS':
                T += 1
                entities_pred['T%i' % T] = {'start':position['start'], 'end':position['end'], 'type':'unknown', 'entity':'Disease', 'text': token}
            elif label == 'I-DIS':
                txt = entities_pred['T%i' % T]['text']
                entities_pred['T%i' % T].update({'end':position['end'], 'text': txt + space + token})
            prev_label = label

    with codecs.open(corpus_pred_output, 'w', encoding='utf-8') as out_file:
        for review in reviews:
            out_file.write(json.dumps(review) + u'\n')



