import json, csv, os, copy, random, logging
from deepdiff import DeepDiff

severity_map = {
    'Major': 'a lot', 
    'Minor': 'somewhat', 
    'Neutral': 'minor',
    'no-error': None
}
reverse_severity_map = {v: k for k, v in severity_map.items()}

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def convert_entry_forward(matching_sentences):
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
            'seg_id': matching_sentences[0]['seg_id'],
            'rater': matching_sentences[0]['rater'],
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


def convert_data_forward(data_path, limit=None):
    data = []
    with open(data_path, 'r', newline='', encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        data = [r for r in reader]

    systems = set([s['system'] for s in data])
    seg_ids = set([s['seg_id'] for s in data])
    raters = set([s['rater'] for s in data])

    if limit: seg_ids = set(list(seg_ids)[:limit])

    ported_data = []
    for system in systems:
        for seg_id in seg_ids:
            for rater in raters:
                matching_sentences = [s for s in data if\
                    s['seg_id'] == seg_id and\
                    s['rater'] == rater and\
                    s['system'] == system\
                ]
                
                new_sent = convert_entry_forward(matching_sentences)

                if new_sent == None: continue

                new_sent.update({
                    'id': len(ported_data) + 1
                })

                if limit and len(ported_data) > limit: break

                ported_data += [new_sent]

    return ported_data

def convert_data_backward(data_path, output_path, limit=None):
    with open(data_path, "r", encoding='utf-8') as f:
        data = json.load(f)

    base_name, extension = os.path.splitext(output_path)
    if extension.lower() != ".tsv":
        raise ValueError(f"File extension should be '.tsv', recieved {output_path}")

    logger.info(f"Saving to {output_path}...")

    raise NotImplementedError()

    headers = []
    ported_data = []
    with open(output_path, mode='w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(headers)
        writer.writerows(ported_data)