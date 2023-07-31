import json, os, copy, random, logging

category_map = {
    'Irrelevant': 'irrelevant',
    'Redundant': 'repetitive',
    'Wrong-Grounding': 'inconsistent',
    'Unverifiable': 'unverifiable',
    'Incoherent': 'incoherent',
    'Missing-Answer': 'missing_answer',
    'Missing-Major-Auxiliary': 'missing_major_auxiliary',
    'Missing-Minor-Auxiliary': 'missing_minor_auxiliary',
}
reverse_category_map = {v: k for k, v in category_map.items()}

def convert_data_forward(data_path, limit=None):
    with open(data_path, "r", encoding='utf-8') as f:
        data = json.load(f)

    if limit: data = data[:limit]

    ported_data = []
    for sent in data:
        if 'feedback' not in sent: continue

        passages = sent['passages']
        if len(passages) == 0: continue

        context = ""
        for passage in passages:
            passage_text = f'\n\n### Passage Title: {passage[0]}'
            for passage_sent in passage[1:]:
                passage_text += "\n" + passage_sent.replace(passage[0] + "\n\n", "")
            context += passage_text

        context += f'\n\n### Question: {sent["question"]}' 

        new_sent = {
            'context': context,
            'source': sent['gold'],
            'target': sent['prediction 1'],
            'edits': []
        }

        for i, edit in enumerate(sent['feedback']['errors']):
            new_edit = {
                'id': i,
                'category': 'factual',
                'annotation': {
                    'factual_error': {
                        'val': category_map[edit['error type']]
                    },
                    'explanation': edit['explanation'] if edit['explanation'] != '' else None
                },
                'output_idx': [[edit['start'], edit['end']]],
            }
            new_sent['edits'] += [new_edit]

        for i, edit in enumerate(sent['feedback']['missing-info']):
            new_edit = {
                'id': i + len(sent['feedback']['errors']),
                'category': 'missing_info',
                'annotation': {
                    'missing_info_error': {
                        'val': category_map[edit['error type']]
                    },
                    "passage_id": str(edit['passage_id']),
                    "sentence_id": str(edit['sentence_id'])
                }
            }
            new_sent['edits'] += [new_edit]

        # TODO: need to add corrected-prediction

        ported_data += [new_sent]
    return ported_data