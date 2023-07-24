<div align="center">
    <img src="./public/logo.png" width="400"/>

[Build an Interface](https://nlproc.tools) | [Video Tutorial](https://www.youtube.com) | [Paper](https://arxiv.org/)
</div>

------------------------------------------------

## Quick Start
Visit [nlproc.tools/?t=demo](https://nlproc.tools/?t=demo) for demo tutorials.

## The `nlproc_tools` Python Package
```python
pip install nlproc_tools
```

## Data Conversion
To convert to our standardized data format, clone our repo and use our conversion scripts. (see [**data**](./data) for more details)
```
git clone https://github.com/davidheineman/nlproc.tools.git
cd nlproc.tools/data
python convert.py --dataset <dataset_name> --data_path <path_to_data> --output_path <path_to_output>
```

To convert back to the original formats:
```
python convert.py --reverse --dataset <dataset_name> --data_path <path_to_data> --output_path <path_to_output>
```

In the table below you can find all the original data for each interface (see [**data**](./data) for more details):

<!-- | year | data | paper |
|:---: | :--: | :---: |
| 2017 | [🔗](https://unbabel-experimental-data-sets.s3.eu-west-1.amazonaws.com/comet/data/2017-da.tar.gz) | [Findings of the 2017 Conference on Machine Translation (WMT17)](https://aclanthology.org/W17-4717.pdf) |
| 2018 | [🔗](https://unbabel-experimental-data-sets.s3.eu-west-1.amazonaws.com/comet/data/2018-da.tar.gz) | [Findings of the 2018 Conference on Machine Translation (WMT18)](https://aclanthology.org/W18-6401.pdf) |
| 2019 | [🔗](https://unbabel-experimental-data-sets.s3.eu-west-1.amazonaws.com/comet/data/2019-da.tar.gz) | [Findings of the 2019 Conference on Machine Translation (WMT19)](https://aclanthology.org/W19-5301.pdf) |
| 2020 | [🔗](https://unbabel-experimental-data-sets.s3.eu-west-1.amazonaws.com/comet/data/2020-da.tar.gz) | [Findings of the 2020 Conference on Machine Translation (WMT20)](https://aclanthology.org/2020.wmt-1.1.pdf) |
| 2021 | [🔗](https://unbabel-experimental-data-sets.s3.eu-west-1.amazonaws.com/comet/data/2021-da.tar.gz) | [Findings of the 2021 Conference on Machine Translation (WMT21)](https://aclanthology.org/2021.wmt-1.1.pdf) |
| 2022 | [🔗](https://unbabel-experimental-data-sets.s3.eu-west-1.amazonaws.com/comet/data/2022-da.tar.gz) | [Findings of the 2022 Conference on Machine Translation (WMT22)](https://aclanthology.org/2022.wmt-1.1.pdf) | -->

## Contributing

### Set up
- Clone this repo: `git clone https://github.com/davidheineman/nlproc.tools.git`
- Set up Vue: `npm install`
- To run a dev environment: `npm run dev`
- When you're done making changes: `npm run build`
- If you want to deploy to GitHub pages: `npm run deploy`. This creates a `gh-pages` branch. You will need to go into GitHub Pages settings and set the source branch to `gh-pages`.

### Submit a New Typology
To add your own dataset permanently on nlproc.tools...

### Add Language Support
To add your own dataset permanently on nlproc.tools...

## Cite nlproc.tools
If you find nlproc.tools helpful, please consider cite our work:
```
@citation
```