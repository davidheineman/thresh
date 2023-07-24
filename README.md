<div align="center">
    <img src="./public/logo.png" width="400"/>

[Build an Interface](https://nlproc.tools) | [Video Tutorial](https://www.youtube.com) | [Paper](https://arxiv.org/)
</div>

------------------------------------------------

## Quick Start
Visit [nlproc.tools/?t=demo](https://nlproc.tools/?t=demo) for demo tutorials.

## The `nlproc-tools` Python Package
```python
pip install nlproc-tools
```

## Data Conversion
To convert to our standardized data format, see [**data**](./data) for more information and links.
```
git clone https://github.com/davidheineman/nlproc.tools.git
cd nlproc.tools/data
python convert.py --dataset <dataset_name> --data_path <path_to_data> --output_path <path_to_output>
```

To convert back to the original formats:
```
python convert.py --reverse --dataset <dataset_name> --data_path <path_to_data> --output_path <path_to_output>
```

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