<div align="center">
    <img src="./public/img/logo.png" width="400"/>

[**Build an Interface**](https://thresh.tools) | [**Video Tutorial**](https://www.youtube.com) | [**Paper**](https://arxiv.org/)
</div>
<br />
<div align="center">
    <img src="./public/img/github-banner.jpg" width="100%" style="max-width: 1000px" />
</div>

------------------------------------------------

## Quick Start
Visit [**thresh.tools/?t=demo**](https://thresh.tools/?t=demo) for demo tutorials.

<a id="deploy"></a>

## Deploy an Interface

## Data Tools
```python
pip install thresh
```

### Loading Annotations
To load annotations, simply load your JSON data and call `load_annotations`:

```python
from thresh import load_interface

# Serialize your typology into a class
YourInterface = load_interface(
    "<path_to_typology>.yml"
)

# Load & serialize data from <file_name>.json
thresh_data = YourInterface.load_annotations(
    "<file_name>.json"
)
```

For example, using the SALSA demo data:
```python
from thresh import load_interface

# Load SALSA data using the SALSA typology
Salsa = load_interface("salsa.yml")
salsa_data = Salsa.load_annotations("salsa.json")

print(salsa_data[0])
>> SalsaEntry(
>>   annotator: annotator_1, 
>>   system: new-wiki-1/Human-2-written, 
>>   source: "Further important aspects of Fungi ...", 
>>   target: "An important aspect of Fungi in Art is ...", 
>>   edits: [
>>     DeletionEdit(
>>       input_idx: [[259, 397]], 
>>       annotation: DeletionAnnotation(
>>         deletion_type: GoodDeletion(
>>           val: 3
>>         ), 
>>         coreference: False, 
>>         grammar_error: False
>>       ),
>>     ), 
>>     ...
>>   ]
>> )
```

To prepare a dataset for annotation, simply export your `List[Annotation]` object and call `export_data`:
```python
# Export data to <file_name>.json for annotation
YourInterface.export_data(
    data=thresh_data,
    filename="<file_name>.json"
)
```

For a full tutorial with examples and advanced usage, please see [**/notebook_tutorials/load_data.ipynb**](./notebook_tutorials/load_data.ipynb).

### Internal Data Classes
Our data loading code is backed by custom internal classes which are created based on your typology. You can access these classes directly:
```python
from thresh import get_entry_class

# Get the custom data class for the SALSA typology
Salsa = load_interface("salsa.yml")
SalsaEntry = Salsa.get_entry_class()

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
pip install thresh
```

To convert to our standardized data format, our library includes bi-directional conversion from existing fine-grained annotation typologies:

```python
from thresh import convert_dataset

# To convert to the thresh.tools standardized format:
thresh_data = convert_dataset(
    data_path="<path_to_original_data>", 
    dataset="<dataset_name>"
)

# To convert back to the original format:
original_data = convert_dataset(
    data=thresh_data, 
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
| FRANK | [🔗](https://github.com/artidoro/frank) | [thresh.tools/frank](https://thresh.tools/frank) | `human_annotations.json` |
| SCARECROW | [🔗](https://yao-dou.github.io/scarecrow) | [thresh.tools/scarecrow](https://thresh.tools/scarecrow) | `grouped_data.csv` |
| MQM | [🔗](https://github.com/google/wmt-mqm-human-evaluation) | [thresh.tools/mqm](https://thresh.tools/mqm) | `mqm_newstest2020_ende.tsv` |
| SALSA | [🔗](https://github.com/davidheineman/salsa) | [thresh.tools/salsa](https://thresh.tools/salsa) | `salsa_test.json` |
| SNaC | [🔗](https://github.com/tagoyal/snac) | [thresh.tools/snac](https://thresh.tools/snac) | `SNaC_data.json` |
| Wu et al., 2023 | [🔗](https://github.com/allenai/FineGrainedRLHF) | [thresh.tools/wu-etal-2023](https://thresh.tools/wu-etal-2023) | `dev_feedback.json` |
| Da San Martino et al., 2019 | [🔗](https://propaganda.qcri.org/) | [thresh.tools/da-san-martino-etal-2019](https://thresh.tools/da-san-martino-etal-2019) | `test/article<X>.labels.tsv` |

We do not create dataloaders for the following interfaces:

| interface | reason |
|:---: | :--: |
| MultiPIT | This is an inspection interface, examples are taken from Table 7 of the [MultiPIT paper](https://aclanthology.org/2022.emnlp-main.631). |
| CWZCC | The example is taken from App. B of the [CWZCC paper](https://aclanthology.org/2020.lrec-1.327). Full dataset is not publically available due to copyright and privacy concerns. |
| ERRANT | ? |

## Contributing

<a id="local"></a>

### Set Up thresh.tools Locally
Clone this repo: 
```sh
git clone https://github.com/davidheineman/thresh.tools.git
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
You do *not* need to do this if you want to use your interface (please see [**Deploy an Interface**](#deploy)). This will add your interface to the thresh.tools homepage!

<div align="left">
    <img src="./public/img/hosted-interface.png" width="100%" style="max-width: 300px" />
</div>

To make your interface available in the thresh.tools interface, please clone this repo and submit a pull request with the following:

1. Add your typology YML file to [**public/templates/**](./public/templates/).
2. Add your demo data JSON file to [**public/data/**](./public/data/). We encourage authors to submit a sample of 50 examples for their full dataset, but this is not required.
3. Modify [**src/main.js**](./src/main.js) to link to your dataset, by adding a line to `templates`:

    ```js
    const templates = [
        { name: "SALSA", path: "salsa", task: "Simplification", hosted: true },
        { name: "Scarecrow", path: "scarecrow", task: "Open-ended Generation", hosted: true },
        ...
        { name: "<display_name>", path: "<your_interface>", task: "<your_task>", hosted: true }
    ]
    ```
    In this case `<your_task>` will correspond to the task you are grouped with. *Note: You can preview your changes by setting up [**thresh.tools locally**](#local)!*
4. Submit a [**pull request**](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) with your changes! Then we will merge with the thresh.tools main branch. Please reach out if you have any questions.

### Add Language Support
Multi-lingual deployment is core to thresh.tools, and we are actively working to add support for more languages. If you would like to add support for a new language (or revise our existing support), our language templates are located in [**public/lang/**](./public/lang/).
- To add support for a new language, simply create a new `.yml` using the structure of an [**existing language template**](./public/lang/en.yml).
- To revise an existing template, simply make changes within the template.

When you are finished, please submit a [**pull request**](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) with your changes.

### Set Up the `thresh` Python Library
Clone this repo: 
```sh
git clone https://github.com/davidheineman/thresh.tools.git
cd data_tools\src
```

Make any changes to the library and push to PyPi:
```sh
rm -r dist 
python -m build
python -m twine upload --repository pypi dist/*
```

## Cite thresh.tools
If you find thresh.tools helpful, please consider cite our work:
```
@citation{
    coming soon!
}
```