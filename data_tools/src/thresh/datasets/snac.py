import json, os, copy, random, logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def find_substring_indices(main_string, substring):
    start_index = main_string.find(substring)
    end_index = start_index + len(substring) if start_index != -1 else -1
    return start_index, end_index

def convert_entry_forward(sent):
    edits = []
    for i, edit in enumerate(sent['errors']):
        start_idx, end_idx = find_substring_indices(sent['text'], edit['span'])

        edits += [{
            'id': i,
            'category': edit['error_type'],
            'output_idx': [[start_idx, end_idx]],
            'votes': edit['votes']
        }]

    return {
        'source': '',
        'target': sent['text'],
        'edits': edits
    }

def convert_data_forward(data_path, limit=None):
    with open(data_path, "r", encoding='utf-8') as f:
        data = json.load(f)

    data = [i for j in [list(x.values()) for x in list(data.values())] for i in j]
    
    if limit:
        random.shuffle(data)
        data = data[:limit]
    
    return [convert_entry_forward(sent) for sent in data]

def convert_entry_backward(sent):
    errors = []
    for edit in sent['edits']:
        errors += [{
            'span': sent['target'][edit['output_idx'][0][0]:edit['output_idx'][0][1]],
            'votes': edit['votes'],
            'error_type': edit['category']
        }]

    return {
        "errors": errors,
        "text": sent['target']
    }

def convert_data_backward(data_path, output_path, limit=None):
    with open(data_path, "r", encoding='utf-8') as f:
        data = json.load(f)

    ported_data = {str(i): convert_entry_backward(sent) for i, sent in enumerate(data)}

    base_name, extension = os.path.splitext(output_path)
    if extension.lower() != ".json":
        raise ValueError(f"File extension should be '.json', recieved {output_path}")

    logger.info(f"Saving to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(ported_data, f, indent=4)
    