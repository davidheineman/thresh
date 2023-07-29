import json, os, copy, random, logging

def convert_data_forward(data_path, limit=None):
    with open(data_path, "r", encoding='utf-8') as f:
        data = json.load(f)

    if limit:
        random.shuffle(data)
        data = data[:limit]

    ported_data = []
    for sent in data:
        errors = [error_list for ann, error_list in sent['summary_sentences_annotations'][0].items()]
        errors = list(set([i for j in errors for i in j if i != 'NoE']))

        # if limit and len(errors) < 2: continue

        edits = []
        for i, error in enumerate(errors):
            edits += [{
                "category": error,
                "id": i,
                "annotation": None
            }]

        new_sent = {
            'context': sent['article'],
            'source': sent['reference'],
            'target': sent['summary'],
            'edits': edits
        }

        ported_data += [new_sent]

    return ported_data