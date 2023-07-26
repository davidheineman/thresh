from .util import verify_exists, to_camel_case, get_sent_keys, get_meta_keys
from .names import Entry
from typing import List
import json, yaml

excluded_cols = ['metadata', 'edits']

def load_annotations(filename: str, typology: str) -> List[Entry]:
    """
    Load a nlproc.tools annotation and serialize it into a custom Entry object.
    """

    # Verify and load files
    verify_exists(filename)
    verify_exists(typology)

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(typology, 'r', encoding='utf-8') as f:
        typology = yaml.safe_load(f)

    # Create a custom Entry class for the typology
    CustomEntry = get_entry_class(typology, data)
    sent_keys, meta_keys = get_sent_keys(data), get_meta_keys(data)

    # Convert each entry
    nlproc_data = []
    for sent in data:
        # Initialize the main columns, excluding columns with custom loading
        sent_data = {k: None for k in sent_keys}
        sent_data.update(sent)

        for col in excluded_cols:
            if col in sent_data:
                sent_data.pop(col)

        # Initialize metadata
        metadata = {k: None for k in meta_keys}
        metadata.update(sent['metadata'])

        # Initialize edits

        sent_kwargs = {}
        sent_kwargs.update(metadata)
        sent_kwargs.update(sent_data)

        nlproc_sent = CustomEntry(**sent_kwargs)

        nlproc_data += [nlproc_sent]

    return nlproc_data


def get_entry_class(typology: dict, data: dict=None) -> Entry:
    """
    Define custom Entry class for interface, with corresponding dataloader
    """
    # Get typology name & convert to class name
    class_name, interface_name = '', ''
    if 'template_name' in typology:
        interface_name = typology['template_name']
        class_name = to_camel_case(interface_name)

    all_keys = []
    if data:
        all_keys = get_sent_keys(data) + get_meta_keys(data)
        all_keys = [_ for _ in all_keys if _ not in excluded_cols]

    # Create custom init function
    def custom_init(self, **kwargs):
        for key in all_keys:
            if key not in kwargs.keys():
                raise ValueError(f"Missing key '{key}' in args. Keys as defined by the '{interface_name}' interface are: {all_keys}")
        for key, value in kwargs.items():
            setattr(self, key, value)
    return type(f'{class_name}Entry', (Entry,), {"__init__": custom_init})


def export_data():
    print("hi")