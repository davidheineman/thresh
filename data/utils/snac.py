import json, os, copy, random, logging

def find_substring_indices(main_string, substring):
    start_index = main_string.find(substring)
    end_index = start_index + len(substring) if start_index != -1 else -1
    return start_index, end_index

def convert_entry(sent):
    new_sent = {
        'source': '',
        'target': sent['text'],
        'edits': []
    }

    for i, edit in enumerate(sent['errors']):
        start_idx, end_idx = find_substring_indices(sent['text'], edit['span'])

        new_edit = {
            'id': i,
            'category': edit['error_type'],
            'output_idx': [[start_idx, end_idx]],
            'votes': edit['votes']
        }

        new_sent['edits'] += [new_edit]

    return new_sent

def convert_data_forward(data, limit=None):
    if type(data) == str:
        with open(data, "r", encoding='utf-8') as f:
            data = json.load(f)

    data = [i for j in [list(x.values()) for x in list(data.values())] for i in j]
    
    if limit:
        data = [s for s in data if len(s['errors']) > 3]
        random.shuffle(data)
        data = data[:limit]

    ported_data = []
    for sent in data:
        ported_data += [convert_entry(sent)]
    
    return ported_data

