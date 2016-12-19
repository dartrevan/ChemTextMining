# coding=utf-8
import sys
import optparse
import codecs
import json
from lxml import etree

def get_terms(item, gold, task, type):
    units = []
    review_id = int(item.get("id"))
    content = item.get("text")
    if gold:
        terms = item.get("entities").values()
    else:
        terms = item.get("entities_pred")
        if terms == None:
            return review_id, 0, units
        terms = terms.values()

    terms_count = 0

    term_set = [] # we don't have to take repeated terms

    for json_term in terms:
        if task == "entity":  # task switch
            if json_term.get("entity") != "Disease":
                    continue

            term_identifier = str(json_term.get("start"))+"_"+str(json_term.get("end"))
            if term_identifier in term_set:
                continue
            term_set.append(term_identifier)

            terms_count += 1

            written_term = json_term.get("text")
            position_from = int(json_term.get("start"))
            position_to = int(json_term.get("end"))
            term = content[position_from:position_to]
            #if written_term != term:
            #    print review_id, "terms does't match [", str(position_from), str(position_to), ") ->", term, "<>", written_term

            units.append(str(position_from)+'_'+str(position_to))

    return review_id, terms_count, units

def get_units(item, gold, task, type):
    units = []
    review_id = int(item.get("id"))
    content = item.get("text")
    if gold:
        terms = item.get("entities").values()
    else:
        terms = item.get("entities_pred")
        if terms == None:
            return review_id, 0, units
        terms = terms.values()

    terms_count = 0

    term_set = [] # we don't have to take repeated terms

    for json_term in terms:
        if task == "entity":  # task switch
            if json_term.get("entity") != "Disease":
                if gold==True:
                    continue

        term_identifier = str(json_term.get("start"))+"_"+ str(json_term.get("end"))

        if term_identifier in term_set:
            continue
        term_set.append(term_identifier)

        terms_count += 1

        written_term = json_term.get("text")
        position_from = int(json_term.get("start"))
        position_to = int(json_term.get("end"))
        term = content[position_from:position_to]
        #if written_term != term:
        #    print review_id, "terms does't match [", str(position_from), str(position_to), ") ->", term, "<>", written_term

        start = position_from
        for i, unit in enumerate(term.split(' ')):
            end = start + len(unit)
            units.append(str(start)+'_'+str(end))
            start = end + 1

    return review_id, terms_count, units

def getAllDocs(f):
    data = []
    with codecs.open(f, encoding="utf-8") as fin:
        for line in fin:
            data.append(json.loads(line))
    return data

def computeEvalNumbers(alg_type, itemlistGS, itemlistTest, task, type):
    print "type\tid\tcorrect_unit_count\textracted_unit_coun\tmatch_count\tp\tr\tf"

    idx2units = {}
    for itm in itemlistGS:
        if alg_type == "weak":
            idx, terms_count, units = get_units(itm, True, task, type)
        else:
            idx, terms_count, units = get_terms(itm, True, task, type)
        if terms_count>0:
            idx2units[idx] = (terms_count, units)
    total_p, total_r, total_f = .0, .0, .0
    processed = []

    for itm in itemlistTest:
        idx = int(itm.get("id"))

        if alg_type == "weak":
            idx, terms_count, units = get_units(itm, False, task, type)
        else:
            idx, terms_count, units = get_terms(itm, False, task, type)

        if idx in idx2units and not idx in processed: #it's not processed test review
            processed.append(idx)
            correct = idx2units[idx][1]
            correct4del = [i for i in correct]
            extracted = units
            match = []
            for i in extracted:
                if i in correct4del:
                    match.append(i)
                    correct4del.remove(i)
            try:
                r = float(len(match))/len(correct)
                p = float(len(match))/len(extracted) if len(extracted) != 0 else 0
                if p == 0 and r == 0:
                    f = 0
                else:
                    f = (2*p*r)/(p+r)
                total_p += p
                total_r += r
                total_f += f
                print "%d\t%d\t%d\t%d\t%.3f\t%.3f\t%.3f" % (idx, len(correct),len(extracted), len(match), p, r, f)
            except:
                print "Unexpected error:", sys.exc_info()[0]
                continue

    n = len(idx2units.keys())
    print "%s\t%f\t%f\t%f" % (type,total_p/n, total_r/n, total_f/n)

def main(argv=None):
    # parse the input
    parser = optparse.OptionParser()
    parser.add_option('-g') #gold standard file
    parser.add_option('-t') #test file with predicted entities
    parser.add_option('-a') #"type" or "entity"
    parser.add_option('-w') #weak or strong evaluation
    options, args = parser.parse_args()
    gold_file_name = options.g
    test_file_name = options.t

    task = options.a
    alg_type = options.w

    # process file with gold markup
    itemlistGS = getAllDocs(gold_file_name)
    itemlistTest = getAllDocs(test_file_name)
    types=[u'none']
    for type in types:
        computeEvalNumbers(alg_type, itemlistGS, itemlistTest, task,type)

if __name__ == "__main__":
    main(sys.argv[1:])
    exit()
