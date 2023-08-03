import json, os, copy, random, logging

def convert_data_forward(data_path, limit=None):
    with open(data_path, "r", encoding='utf-8') as f:
        data = json.load(f)

    data = [data[str(i)] for i in range(len(data))]
    if limit: random.shuffle(data)

    ported_data = []
    for sent in data:
        edits = []
        edit_list = [sent['edits-combination-0'][str(i)] for i in range(len(sent['edits-combination-0']))]
        for i, input_edit in enumerate(edit_list):
            edit = {
                "category": input_edit['type'],
                "id": i,
                "annotation": None
            }

            if input_edit['sentence-1-token-indices'] is not None:
                start_token, end_token = input_edit['sentence-1-token-indices']
                start_idx = sum([len(x) + 1 for x in sent['sentence-1'].split(' ')[:start_token]])
                end_idx = start_idx + sum([len(x) + 1 for x in sent['sentence-1'].split(' ')[start_token:end_token]])
                edit['input_idx'] = [[start_idx, end_idx]]
            if input_edit['sentence-2-token-indices'] is not None:
                start_token, end_token = input_edit['sentence-2-token-indices']
                start_idx = sum([len(x) + 1 for x in sent['sentence-2'].split(' ')[:start_token]])
                end_idx = start_idx + sum([len(x) + 1 for x in sent['sentence-2'].split(' ')[start_token:end_token]])
                edit['output_idx'] = [[start_idx, end_idx]]

            if input_edit['intention'] is not None:
                input_intention = input_edit['intention'].lower()
                edit['annotation'] = {
                    "intention": {
                        "val": input_intention
                    }
                }
                if 'lang' in input_intention:
                    edit['annotation'] ={
                        "intention": {
                            "val": "lang",
                            "lang": {
                                "val": input_intention.replace('lang-', '')
                            }
                        }
                    }

            edits += [edit]

        new_sent = {
            'source': sent['sentence-1'],
            'target': sent['sentence-2'],
            'metadata': {
                'easy-or-hard': sent['easy-or-hard'],
                'sentence-pair-index': sent['sentence-pair-index'],
                'arxiv-id': sent['arxiv-id'],
                'sentence-1-level': sent['sentence-1-level'],
                'sentence-2-level': sent['sentence-2-level'],
            },
            'edits': edits
        }

        ported_data += [new_sent]

    if limit: ported_data = ported_data[:limit]

    return ported_data