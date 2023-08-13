import json, os, copy, random, logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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
                "category": input_edit['type'].lower(),
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

        ported_data += [{
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
        }]

    if limit: ported_data = ported_data[:limit]

    return ported_data

def convert_entry_backward(sent):
    edits = []
    for edit in sent['edits']:
        annotation = edit['annotation']['intention']['val'] # TODO: capitalize this
        if 'lang' in annotation:
            annotation = f"lang-{edit['annotation']['intention']['lang']['val']}"

        converted_edit = {
            'type': edit['category'], # TODO: capitalize this
            'intention': annotation
        }

        if 'input_idx' in edit:
            converted_edit.update({
                'sentence-1-token-indices': [
                    len(sent['source'][:edit['input_idx'][0][0]].split(' '))-1,
                    len(sent['source'][:edit['input_idx'][0][1]].split(' '))-1
                ]
            })
        if 'output_idx' in edit:
            converted_edit.update({
                'sentence-2-token-indices': [
                    len(sent['target'][:edit['output_idx'][0][0]].split(' '))-1,
                    len(sent['target'][:edit['output_idx'][0][1]].split(' '))-1
                ]
            })

        edits += [converted_edit]

    return {
        "easy-or-hard": sent['metadata']["easy-or-hard"],
        "sentence-pair-index": sent['metadata']['sentence-pair-index'],
        "sentence-1": sent["source"],
        "sentence-2": sent["target"],
        "edits-combination-0": {str(i): e for i, e in enumerate(edits)},
        "arxiv-id": sent['metadata']['arxiv-id'],
        "sentence-1-level": sent['metadata']['sentence-1-level'],
        "sentence-2-level": sent['metadata']['sentence-2-level']
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
    