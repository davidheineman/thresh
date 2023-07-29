import json, csv, os, copy, random, logging, ast

severity_map = {
    1: 'minor',
    2: 'somewhat',
    3: 'a lot'
}
reverse_severity_map = {v: k for k, v in severity_map.items()}

def convert_data_forward(data_path, limit=None):
    data = []
    with open(data_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [r for r in reader]

    if limit: data = data[:limit]

    ported_data = []
    for sent in data:
        new_sent = {}

        new_sent.update({
            'id': len(ported_data) + 1,
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

        # Add Edits
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
                'id': len(new_edit) - 1,
                'category': ann_type,
                'output_idx': output_idx,
            })

            new_edit['annotation'] = {
                'explanation': explanation.replace('_SEP_', ',').replace('_QUOTE_', '"'),
                ann_type_label: severity_map[severity]
            }

            new_sent['edits'] += [new_edit]
        ported_data += [new_sent]

    return ported_data