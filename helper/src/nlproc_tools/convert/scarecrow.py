from deepdiff import DeepDiff

filename = 'scarecrow/scarecrow.csv'

def load_scarecrow(filename):
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [r for r in reader]
    return data

data = load_scarecrow(filename)

data = data[:50]

ported_data = []

severity_map = {
    1: 'minor',
    2: 'somewhat',
    3: 'a lot'
}

i = 1
for sent in data:
    new_sent = {}

    new_sent.update({
        'id': i,
        'metadata': {
            'gid': sent['gid'],
            'model': sent['model'],
            'p': sent['p'],
            'temperature': sent['temperature'],
            'frequency_penalty': sent['frequency_penalty'],
        },
        'source': sent['prompt'],
        'target': sent['generation'],
        'edits': []
    })

    annotations = ast.literal_eval(sent['responses'])
    # SCARECROW collected 10 annotations

    # Add Edits
    j = 0
    for edit in annotations[4]:
        new_edit = {}
        type_, explanation, severity, start_idx, end_idx, antacedents = edit

        ann_type = type_.lower().replace('-', '_').replace(' ', '_')
        ann_type_label = f'{ann_type}_type'

        output_idx = [[start_idx, end_idx]]

        if len(antacedents) > 0:
            for i in range(len(antacedents) // 2):
                start_idx, end_idx = antacedents[2 * i], antacedents[2 * i + 1]
                output_idx += [[start_idx, end_idx]]

        new_edit.update({
            'id': j,
            'category': ann_type,
            'output_idx': output_idx,
        })

        new_edit['annotation'] = {
            'explaination': explanation.replace('_SEP_', ',').replace('_QUOTE_', '"'),
            ann_type_label: severity_map[severity]
        }

        new_sent['edits'] += [new_edit]
        j += 1
    ported_data += [new_sent]
    i += 1

with open('../public/data/scarecrow.json', 'w') as f:
    json.dump(ported_data, f, indent=4)