import json, csv, os, copy, random, logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

category_map = {
    'Loaded_Language': 'loaded_language',
    'Name_Calling,Labeling': 'name_calling',
    'Repetition': 'repetition',
    'Exaggeration,Minimisation': 'exaggeration',
    'Doubt': 'doubt',
    'Appeal_to_fear-prejudice': 'appeal_to_fear_prejudice',
    'Flag-Waving': 'flag_waving',
    'Causal_Oversimplification': 'causal_oversimplification',
    'Slogans': 'slogans',
    'Appeal_to_Authority': 'appeal_to_authority',
    'Black-and-White_Fallacy': 'black_and_white_fallacy',
    'Thought-terminating_Cliches': 'thought_terminating_cliches',
    'Whataboutism': 'whataboutism',
    'Reductio_ad_hitlerum': 'reductio_ad_hitlerum',
    'Red_Herring': 'red_herring',
    'Bandwagon': 'bandwagon',
    'Obfuscation,Intentional_Vagueness,Confusion': 'obfuscate',
    'Straw_Men': 'straw_man'
}
reverse_category_map = {v: k for k, v in category_map.items()}

def load_propaganda(filename):
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as tsv_file:
        reader = csv.reader(tsv_file, delimiter="\t")
        data = [r for r in reader]
    return data

def convert_entry_forward(filename):
    label_filename = f'{filename}.labels.tsv'
    text_filename = f'{filename}.txt'
    annotations = load_propaganda(label_filename)

    article_id = int(os.path.basename(filename).replace('article', ''))

    with open(text_filename, "r", encoding='utf-8') as f:
        article = f.read()

    edits = []
    for i, ann in enumerate(annotations):
        edit = {
            'category': category_map[ann[1]],
            'id': i,
            'output_idx': [[int(ann[2]), int(ann[3])]]
        }
        edits += [edit]

    return {
        'source': '',
        'target': article,
        'metadata': {
            'article_id': article_id
        },
        'edits': edits
    }

def convert_data_forward(data_path, limit=None):
    """
    Note: dir_path should correspond to a folder containing pairs of .txt and .labels.tsv files.
    """
    article_names = set([data_path + x.replace('.txt', '').replace('.labels.tsv', '') for x in os.listdir(data_path) if 'article' in x])

    if limit:
        article_names = list(article_names)[:limit]
        random.shuffle(article_names)

    ported_data = []
    for filename in article_names:
        ported_data += [convert_entry_forward(filename)]

    return ported_data

def convert_entry_backward(sent):
    labels = []
    for edit in sent['edits']:
        labels += [[
            reverse_category_map[edit['category']],
            edit['output_idx'][0][0],
            edit['output_idx'][0][1]
        ]]

    return {
        'labels': labels,
        'article': sent['target'],
        'id': sent['metadata']['article_id']
    }

def convert_data_backward(data_path, output_path, limit=None):
    with open(data_path, "r", encoding='utf-8') as f:
        data = json.load(f)

    ported_data = [convert_entry_backward(sent) for sent in data]

    logger.info(f"Saving to the {output_path} folder...")

    if not os.path.isdir(output_path):
        raise ValueError(f"Propaganda saves a folder of files for each article, recieved {output_path}")

    for entry in ported_data:
        i = entry['id']
        logger.info(f"Saving article {i} to {output_path}article{i}...")

        with open(os.path.join(output_path, f"article{i}.txt"), 'w', encoding='utf-8') as f:
            f.write(entry['article'])

        for j, label in enumerate(entry['labels']):
            entry['labels'][j] = [i] + label

        with open(os.path.join(output_path, f"article{i}.labels.tsv"), mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(entry['labels'])
