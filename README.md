<div align="center">
    <img src="./public/logo.png" width="400"/>

[**Build an Interface**](https://nlproc.tools) | [**Video Tutorial**](https://www.youtube.com) | [**Paper**](https://arxiv.org/)
</div>

------------------------------------------------

## Quick Start
Visit [**nlproc.tools/?t=demo**](https://nlproc.tools/?t=demo) for demo tutorials.

## Data Tools
```python
pip install nlproc_tools
```

To load annotations, simply load your JSON data and call `load_annotations`:

```python
from nlproc_tools import load_annotations

# Load & serialize data from <file_name>.json
nlproc_data = load_annotations(
    filename="<file_name>.json",
    typology="<path_to_typology>.yml"
)
```

To prepare a dataset for annotation, simply export your `List[Annotation]` object and call `export_data`:
```python
from nlproc_tools import export_data

# Export data to <file_name>.json for annotation
export_data(
    data=nlproc_data,
    filename="<file_name>.json",
    typology="<path_to_typology>.yml"
)
```

### Internal Data Classes
Our data loading code is backed by custom internal classes which are created based on your typology. You can access these classes directly:
```python
from nlproc_tools import get_entry_class

# Get the custom data class for the SALSA typology
SalsaEntry = get_entry_class("salsa.yml")

# Create a new entry
custom_entry = SalsaEntry(
    annotator = annotator_1, 
    system = new-wiki-1/GPT-3-zero-shot, 
    target = The film has made more than $552 million at the box office and is currently the eighth most successful movie of 2022., 
    source = The film has grossed over $552 million worldwide, becoming the eighth highest-grossing film of 2022.
)

print(custom_entry.system)
>> new-wiki-1/GPT-3-zero-shot
```

## Data Conversion
```python
pip install nlproc_tools
```

To convert to our standardized data format, our library includes bi-directional conversion from existing fine-grained annotation typologies:

```python
from nlproc_tools import convert_dataset

# To convert to the nlproc.tools standardized format:
nlproc_data = convert_dataset(
    data=original_data, 
    dataset="<dataset_name>"
)

# To convert back to the original format:
original_data = convert_dataset(
    data=nlproc_data, 
    dataset="<dataset_name>", 
    reverse=True
)
```

We support conversion for the following datasets:
```
frank, scarecrow, mqm, snac, wu-etal-2023, da-san-martino-etal-2019
```

### Demo Data Sources

In the table below you can find all the original data for each interface. For our demo data, we randomly selected 50 annotations from each dataset. We include the file names of the specific datsets we use below, selecting from the test set when applicable:

| interface | data | implementation | file name |
|:---: | :--: | :---: | :---: |
| FRANK | [🔗](https://github.com/artidoro/frank) | [nlproc.tools/frank](https://nlproc.tools/frank) | `human_annotations.json` |
| SCARECROW | [🔗](https://yao-dou.github.io/scarecrow) | [nlproc.tools/scarecrow](https://nlproc.tools/scarecrow) | `grouped_data.csv` |
| MQM | [🔗](https://github.com/google/wmt-mqm-human-evaluation) | [nlproc.tools/mqm](https://nlproc.tools/mqm) | `mqm_newstest2020_ende.tsv` |
| SALSA | [🔗](https://github.com/davidheineman/salsa) | [nlproc.tools/salsa](https://nlproc.tools/salsa) | `salsa_test.json` |
| SNaC | [🔗](https://github.com/tagoyal/snac) | [nlproc.tools/snac](https://nlproc.tools/snac) | `SNaC_data.json` |
| Wu et al., 2023 | [🔗](https://github.com/allenai/FineGrainedRLHF) | [nlproc.tools/wu-etal-2023](https://nlproc.tools/wu-etal-2023) | `dev_feedback.json` |
| Da San Martino et al., 2019 | [🔗](https://propaganda.qcri.org/) | [nlproc.tools/da-san-martino-etal-2019](https://nlproc.tools/da-san-martino-etal-2019) | `test/article<X>.labels.tsv` |

We do not create dataloaders for the following interfaces:

| interface | reason |
|:---: | :--: |
| MultiPIT | This is an inspection interface, examples are taken from Table 7 of the [MultiPIT paper](https://aclanthology.org/2022.emnlp-main.631). |
| CWZCC | The example is taken from App. B of the [CWZCC paper](https://aclanthology.org/2020.lrec-1.327). Full dataset is not publically available due to copyright and privacy concerns. |
| ERRANT | ? |

## Contributing

### Set Up nlproc.tools Locally
Clone this repo: 
```sh
git clone https://github.com/davidheineman/nlproc.tools.git
```

Set up Vue: 
```sh
npm install
npm run dev     # To run a dev environment
npm run build   # To build a prod environment in ./build
npm run deploy  # Push to gh-pages
```

Deployment will create a `gh-pages` branch. You will need to go into GitHub Pages settings and set the source branch to `gh-pages`.

### Submit a New Typology
To add your own dataset permanently on nlproc.tools...

### Add Language Support
To add your own dataset permanently on nlproc.tools...

## Cite nlproc.tools
If you find nlproc.tools helpful, please consider cite our work:
```
@citation
```