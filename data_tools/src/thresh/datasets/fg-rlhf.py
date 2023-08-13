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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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

        edits = []
        for i, edit in enumerate(sent['feedback']['errors']):
            edits += [{
                'id': i,
                'category': 'factual',
                'annotation': {
                    'factual_error': {
                        'val': category_map[edit['error type']]
                    },
                    'explanation': edit['explanation'] if edit['explanation'] != '' else None
                },
                'output_idx': [[edit['start'], edit['end']]],
            }]

        for i, edit in enumerate(sent['feedback']['missing-info']):
            edits += [{
                'id': i + len(sent['feedback']['errors']),
                'category': 'missing_info',
                'annotation': {
                    'missing_info_error': {
                        'val': category_map[edit['error type']]
                    },
                    "passage_id": str(edit['passage_id']),
                    "sentence_id": str(edit['sentence_id'])
                }
            }]

        ported_data += [{
            'context': context,
            'source': sent['gold'],
            'target': sent['prediction 1'],
            'edits': edits
        }]
    return ported_data

def convert_entry_backward(sent):
    context = sent['context'].split('\n\n### Question: ')
    passages, question = context[0], context[1]

    ported_passages = [p.split("\n") for p in passages.split('\n\n### Passage Title: ')[1:]]

    errors, missing_info = [], []
    for edit in sent['edits']:
        if edit['category'] == 'factual':
            errors += [{
                'error type': reverse_category_map[edit['annotation']['factual_error']['val']],
                'explanation': edit['annotation']['explanation'],
                'start': edit['output_idx'][0][0],
                'end': edit['output_idx'][0][1]
            }]
        elif edit['category'] == 'missing_info':
            missing_info += [{
                'error type': reverse_category_map[edit['annotation']['missing_info_error']['val']],
                'passage_id': edit['annotation']['passage_id'],
                'sentence_id': edit['annotation']['sentence_id']
            }]

    return {
        'question': question,
        'passages': [ported_passages],
        'gold': sent['source'],
        'prediction 1': sent['target'],
        'prediction 2': '',
        'prediction 3': '',
        'prediction 4': '',
        'feedback': {
            'errors': errors,
            'missing-info': missing_info
            # 'corrected-prediction': corrected_prediction
        }
        # 'preference': []
    }

def convert_data_backward(data_path, output_path, limit=None):
    with open(data_path, "r", encoding='utf-8') as f:
        data = json.load(f)

    ported_data = [convert_entry_backward(sent) for sent in data]

    base_name, extension = os.path.splitext(output_path)
    if extension.lower() != ".json":
        raise ValueError(f"File extension should be '.json', recieved {output_path}")

    logger.info(f"Saving to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(ported_data, f, indent=4)