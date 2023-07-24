## Data Ingestion
Since we create a standardized format for fine-grained annotation, this folder includes data ingestion scripts for existing fine-grained datasets. To run a script use the command:

`python convert.py --dataset <dataset_name> --data_path <path_to_data> --output_path <path_to_output>`

To encourage compatibility, all our scripts are reversible. To convert a dataset collected with nlproc.tools back to the format of the original interface, use the same command with a `--reverse` flag:

`python convert.py --reverse --dataset <dataset_name> --data_path <path_to_data> --output_path <path_to_output>`

For our demo data, we randomly select 50 samples, unless <50 are available. 

### Data Sources
For these interfaces, publically available data is at:
- FRANK - [github.com/artidoro/frank](github.com/artidoro/frank)
    - We sample from `human_annotations.json`
- SCARECROW - [yao-dou.github.io/scarecrow](https://yao-dou.github.io/scarecrow/)
    - i.e., `grouped_data.csv`
- MQM - [github.com/google/wmt-mqm-human-evaluation](https://github.com/google/wmt-mqm-human-evaluation)
    - For our demo data, we use `mqm_newstest2020_ende.tsv`
- SALSA - [github.com/davidheineman/salsa](https://github.com/davidheineman/salsa)
    - For our demo data, we select from the test split
- SNaC - [github.com/tagoyal/snac](https://github.com/tagoyal/snac)
    - More specifically the data is linked [here](https://drive.google.com/file/d/1ff-pV2sX9XNDMdaPxY7v22T2i0235tcE/view) (i.e., `SNaC_data.json`)
- Wu et al., 2023 - [github.com/allenai/FineGrainedRLHF](https://github.com/allenai/FineGrainedRLHF)
    - For our demo data, we select from the dev split (i.e., `dev_feedback.json`)
- Da San Martino et al., 2019 - [propaganda.qcri.org](https://propaganda.qcri.org/)
    - For our demo data, we select from the test split (i.e., `test/article<X>.labels.tsv`)


We do not create dataloaders for the following interfaces:
- MultiPIT - This is an inspection interface, examples are taken from Table 7 of the [MultiPIT paper](https://aclanthology.org/2022.emnlp-main.631).
- CWZCC - The example is taken from App. B of the [CWZCC paper](https://aclanthology.org/2020.lrec-1.327). Full dataset is not publically available due to copyright and privacy concerns.
- ERRANT?