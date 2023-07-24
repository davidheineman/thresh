filename = 'frank/human_annotations_sentence.json'

with open(filename, "r", encoding='utf-8') as f:
    data = json.load(f)

random.shuffle(data)

ported_data = []
for sent in data:
    errors = [error_list for ann, error_list in sent['summary_sentences_annotations'][0].items()]
    errors = list(set([i for j in errors for i in j if i != 'NoE']))

    if len(errors) < 2: continue

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

ported_data = ported_data[:50]

with open('../public/data/frank.json', 'w') as f:
    json.dump(ported_data, f, indent=4)