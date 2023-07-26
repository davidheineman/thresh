from deepdiff import DeepDiff

filename = 'mqm/mqm_newstest2020_ende.tsv'

def load_mqm(filename):
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        data = [r for r in reader]
    return data

data = load_mqm(filename)

severity_map = {
    'Major': 'a lot', 
    'Minor': 'somewhat', 
    'Neutral': 'minor',
    'no-error': None
}

systems = set([s['system'] for s in data])

seg_ids = set([s['seg_id'] for s in data])
seg_ids = set(list(seg_ids)[:20])

raters = set([s['rater'] for s in data])

ported_data = []

def process_sentences(matching_sentences):
    new_sent = {}
    sources, targets = [s['source'] for s in matching_sentences], [s['target'] for s in matching_sentences]

    if len(sources) == 0 or len(targets) == 0:
        return None

    assert len(set(sources)) == 1, sources
    source = sources[0]
    target = targets[0].replace('<v>', '').replace('</v>', '')

    new_sent.update({
        'metadata': {
            'system': matching_sentences[0]['system'],
            'doc': matching_sentences[0]['doc'],
            'seg_id': seg_id,
            'rater': rater,
        },
        'source': source,
        'target': target,
        'edits': []
    })

    # Add Edits
    j_id = 0
    for j in range(len(targets)):
        target = targets[j]
        target_data = matching_sentences[j]

        start_tag, end_tag = '<v>', '</v>'
        start_idx = target.find(start_tag)
        end_idx = target.find(end_tag) - len(start_tag)

        if start_idx == -1 or end_idx == -1:
            return None

        severity = target_data['severity']

        category = target_data['category'].replace('Style/Awkward', 'akward').split('/')

        type_ = category[0]
        sub_type = None
        if len(category) > 1:
            sub_type = category[1]

        type_label = type_.lower().replace('-', '_').replace(' ', '_')

        edit_annotation = {
            'id': j_id,
            'category': type_label,
            'output_idx': [[start_idx, end_idx]],
        }

        ann_type_label = f'{type_label}_type'

        if sub_type == None:
            edit_annotation['annotation'] = {
                ann_type_label: severity_map[severity]
            }
        else:
            sub_type_label = sub_type.lower().replace('-', '_').replace(' ', '_')
            edit_annotation['annotation'] = {
                ann_type_label: {
                    'val': sub_type_label,
                    sub_type_label: severity_map[severity]
                }
            }

        if severity != 'no-error':
            exists = False
            for existing_edit in new_sent['edits']:
                ee_copy = copy.deepcopy(existing_edit)
                en_copy = copy.deepcopy(edit_annotation)
                ee_copy['id'] = en_copy['id']
                diff = DeepDiff(ee_copy, en_copy) # very slow
                if not diff:
                    exists = True
            if not exists:
                new_sent['edits'] += [edit_annotation]
        
        j_id += 1
    return new_sent

i = 1
for system in systems:
    for seg_id in seg_ids:
        for rater in raters:
            matching_sentences = [s for s in data if\
                s['seg_id'] == seg_id and\
                s['rater'] == rater and\
                s['system'] == system\
            ]
            
            new_sent = process_sentences(matching_sentences)

            if new_sent == None: continue

            new_sent.update({
                'id': i
            })

            if i > 50: break

            ported_data += [new_sent]

            i += 1

with open('../public/data/mqm.json', 'w') as f:
    json.dump(ported_data, f, indent=4)