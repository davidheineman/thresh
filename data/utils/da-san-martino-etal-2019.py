from deepdiff import DeepDiff

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

def load_propaganda(filename):
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as tsv_file:
        reader = csv.reader(tsv_file, delimiter="\t")
        data = [r for r in reader]
    return data

def load_article(filename):
    label_filename = f'{filename}.labels.tsv'
    text_filename = f'{filename}.txt'
    annotations = load_propaganda(label_filename)

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
        'edits': edits
    }

dirpath = 'da-san-martino-etal-2019/test/'
article_names = set([dirpath+x.replace('.txt', '').replace('.labels.tsv', '') for x in os.listdir(dirpath) if 'article' in x])

article_names = list(article_names)[:50]
random.shuffle(article_names)

ported_data = []
for name in article_names:
    article = load_article(name)
    ported_data += [article]

with open('../public/data/da-san-martino-etal-2019.json', 'w') as f:
    json.dump(ported_data, f, indent=4)