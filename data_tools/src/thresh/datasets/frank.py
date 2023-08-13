import json, os, copy, random, logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def convert_data_forward(data_path, limit=None):
    with open(data_path, "r", encoding='utf-8') as f:
        data = json.load(f)

    if limit:
        random.shuffle(data)
        data = data[:limit]

    ported_data = []
    for sent in data:
        errors = [error_list for ann, error_list in sent['summary_sentences_annotations'][0].items()]
        errors = list(set([i for j in errors for i in j if i != 'NoE']))

        # if limit and len(errors) < 2: continue

        edits = []
        for i, error in enumerate(errors):
            edits += [{
                "category": error,
                "id": i,
                "annotation": None
            }]

        new_sent = {
            'context': sent['article'],
            'source': sent['reference'],
            'target': sent['summary'],
            'metadata': {
                'hash': sent['hash'],
                'model_name': sent['model_name']
            },
            'edits': edits
        }

        ported_data += [new_sent]

    return ported_data

def convert_entry_backward(sent):
    errors = [e['category'] for e in sent['edits']]

    return {
        'hash': sent['metadata']['hash'],
        'model_name': sent['metadata']['hash'],
        'article': sent['context'],
        'summary': sent['target'],
        'reference': sent['source'],
        'summary_sentences_annotations': [{
            "annotator_0": errors
        }]
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