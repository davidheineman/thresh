import json, csv, os, copy, random, logging, ast

severity_map = {
    1: 'minor',
    2: 'somewhat',
    3: 'a lot'
}
reverse_severity_map = {v: k for k, v in severity_map.items()}

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def convert_data_forward(data_path, limit=None):
    data = []
    with open(data_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [r for r in reader]

    if limit: data = data[:limit]

    ported_data = []
    for sent in data:
        annotations = ast.literal_eval(sent['responses'])

        # Add Edits
        edits = []
        for edit in annotations[4]:
            type_, explanation, severity, start_idx, end_idx, antacedents = edit

            ann_type = type_.lower().replace('-', '_').replace(' ', '_')
            output_idx = [[start_idx, end_idx]]

            if len(antacedents) > 0:
                for i in range(len(antacedents) // 2):
                    start_idx, end_idx = antacedents[2 * i], antacedents[2 * i + 1]
                    output_idx += [[start_idx, end_idx]]

            edits += [{
                'id': len(edits) + 1,
                'category': ann_type,
                'output_idx': output_idx,
                'annotation': {
                    'explanation': explanation.replace('_SEP_', ',').replace('_QUOTE_', '"'),
                    f'{ann_type}_type': severity_map[severity]
                }
            }]

        ported_data += [{
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
            'edits': edits
        }]

    return ported_data

def convert_entry_backward(sent):
    annotations = []
    for edit in sent['edits']:
        edit_type = edit['category']
        
        antacedents = []
        for antacedent in edit['output_idx'][1:]:
            antacedents += [antacedent[0]] + [antacedent[1]]

        annotations += [
            edit_type,
            edit['annotation']['explanation'].replace(',', '_SEP_').replace('"', '_QUOTE_'),
            reverse_severity_map[edit['annotation'][f"{edit['category']}_type"]],
            edit['output_idx'][0][0],
            edit['output_idx'][0][1],
            antacedents
        ]
    
    return [
        sent['id'],
        sent['metadata']['gid'],
        sent['source'],
        sent['target'],
        sent['metadata']['model'],
        sent['metadata']['p'],
        sent['metadata']['temperature'],
        sent['metadata']['frequency_penalty'],
        str(annotations)
    ]

def convert_data_backward(data_path, output_path, limit=None):
    with open(data_path, "r", encoding='utf-8') as f:
        data = json.load(f)

    ported_data = [convert_entry_backward(sent) for sent in data]

    headers = ['id', 'gid', 'prompt', 'generation', 'p', 'temperature', 'frequency_penalty', 'responses']

    base_name, extension = os.path.splitext(output_path)
    if extension.lower() != ".csv":
        raise ValueError(f"File extension should be '.csv', recieved {output_path}")

    logger.info(f"Saving to {output_path}...")

    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(ported_data)
