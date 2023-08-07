from .util import verify_exists, to_camel_case, get_sent_keys, get_meta_keys
from .names import Entry, Edit, Interface
from typing import List
import json, yaml


def load_interface(typology_dict: str) -> Interface:
    """
    Load a thresh.tools interface given its typology
    """

    # Verify and load files
    verify_exists(typology_dict)
    with open(typology_dict, 'r', encoding='utf-8') as f:
        typology_dict = yaml.safe_load(f)

    class_name, interface_name = '', ''
    if 'template_name' in typology_dict:
        interface_name = typology_dict['template_name']
        class_name = to_camel_case(interface_name)

    if 'edits' not in typology_dict.keys():
        raise ValueError("Typology must contain 'edits' key.")

    # Create custom init function
    def custom_init(self, typology: dict):
        for key, value in typology.items():
            setattr(self, key, value)
        self.entry_class = self.create_entry_class()

        # Create classes for each edit
        primitive_edits = [e for e in self.edits if 'type' not in e.keys() or (e['type'] == 'single_span' or e['type'] == 'multi_span') ]
        composite_edits = [e for e in self.edits if 'type' in e.keys() and e['type'] == 'composite']

        self.edit_classes = {}
        self.annotation_classes = {}

        primitive_edit_classes = {k: self.create_edit_class(k) for k in set([e['name'] for e in primitive_edits])}
        self.edit_classes.update(primitive_edit_classes)

        composite_edit_classes = {k: self.create_edit_class(k) for k in set([e['name'] for e in composite_edits])}
        self.edit_classes.update(composite_edit_classes)

    # Create typology class
    TypologyClass = type(f'{class_name}', (Interface,), {"__init__": custom_init})

    typology_loaded = TypologyClass(typology=typology_dict)

    return typology_loaded
