from .util import verify_exists, to_camel_case, get_sent_keys, get_meta_keys, format_class_str
from abc import ABC, abstractmethod
from typing import Union, List
import json, yaml, logging, os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

excluded_sent_cols = ['metadata', 'edits', '_thresh_id']      # <- Exclude this from key checking for Entry
excluded_edit_cols = ['id', 'category']                             # <- Exclude this from key checking for Edit

# Manually specify strings to convert to primitive Python values
value_map = {
    'yes': True,
    'no': False,
    'a lot': 3,
    'somewhat': 2,
    'minor': 1,
}
reverse_value_map = {v: k for k, v in value_map.items()}

    
class Annotation:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        attributes = ", ".join(f"\n  {k}: {format_class_str(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attributes}\n)"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        converted_annotation = {}

        for k, v in self.__dict__.items():
            new_value = v
            if isinstance(v, Annotation):
                subannotation_name = v.__annotationname__()
                new_value = {
                    'val': subannotation_name,
                    subannotation_name: v.to_dict()
                }
                if isinstance(new_value[subannotation_name]['val'], str) and new_value[subannotation_name]['val'] in value_map.keys():
                    new_value[subannotation_name] = new_value[subannotation_name]['val']
            elif v in reverse_value_map.keys():
                new_value = reverse_value_map[v]
            converted_annotation.update({k: new_value})

        return converted_annotation


class Edit:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        attributes = ", ".join(f"\n  {k}: {format_class_str(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attributes}\n)"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        converted_edit = {k: getattr(self, k) for k in self.__dict__.keys() if k not in ['annotation', 'constituent_edits']}
        converted_edit.update({'category': self.__editname__()})

        if hasattr(self, 'annotation'):
            converted_edit.update({'annotation': self.annotation.to_dict()})

        if hasattr(self, 'constituent_edits'):
            converted_edit.update({'constituent_edits': [e.to_dict() for e in self.constituent_edits]})
            
        return converted_edit

    def flatten() -> None:
        raise NotImplementedError()


class Entry:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        attributes = ", ".join(f"\n  {k}: {format_class_str(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attributes}\n)"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        excluded_cols = excluded_sent_cols
        if hasattr(self, '__metakeys__'):
            excluded_cols += self.__metakeys__()

        # Add sentence-level data
        converted_sent = {k: getattr(self, k) for k in self.__dict__.keys() if k not in excluded_cols}
        
        # Add metadata
        if hasattr(self, '__metakeys__'):
            converted_sent.update({'metadata': {k: getattr(self, k) for k in self.__metakeys__()}})

        # Add edits
        if hasattr(self, 'edits') and self.edits is not None:
            converted_edits = []
            for edit in self.edits:
                converted_edits += [edit.to_dict()]
            converted_sent.update({'edits': converted_edits})

        return converted_sent


class Interface:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        attributes = ", ".join(f"\n  {k}: {format_class_str(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attributes}\n)"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self, data: List[Entry]) -> dict:
        """
        Convert interface data back to a json for export.
        """
        return [entry.to_dict() for entry in data]

    def load_annotations(self, data_or_filename: Union[str, dict]) -> List[Entry]:
        """
        Load a thresh.tools annotation and serialize it into a custom Entry object.
        """

        # Verify and load files
        if isinstance(data_or_filename, str):
            filename = data_or_filename
            verify_exists(filename)
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = data_or_filename

        # Re-create the custom Entry class given the data
        self.entry_class = self.create_entry_class(data)
        sent_keys, meta_keys = get_sent_keys(data), get_meta_keys(data)

        # Convert each entry
        thresh_data = []
        for sent in data:
            # Initialize the main columns, excluding columns with custom loading
            sent_data = {k: None for k in sent_keys}
            sent_data.update(sent)

            for col in excluded_sent_cols:
                if col in sent_data:
                    sent_data.pop(col)

            # Initialize metadata
            metadata = {k: None for k in meta_keys}
            if 'metadata' in sent.keys():
                metadata.update(sent['metadata'])

            # Initialize edits
            if 'edits' in sent.keys():
                thresh_edits = []
                for edit in sent['edits']:
                    if 'category' not in edit.keys():
                        continue
                    EditClass = self.edit_classes[edit['category']]
                    thresh_edit = EditClass(**{k: v for k, v in edit.items() if k not in excluded_edit_cols})
                    thresh_edits += [thresh_edit]

            sent_kwargs = {}
            sent_kwargs.update(metadata)
            sent_kwargs.update(sent_data)
            sent_kwargs.update({'edits': thresh_edits})

            thresh_sent = self.entry_class(**sent_kwargs)

            thresh_data += [thresh_sent]

        return thresh_data

    def create_entry_class(self, data: dict=None) -> Entry:
        """
        Define custom Entry class for interface, with corresponding dataloader
        """
        # Get typology name & convert to class name
        class_name, interface_name = '', ''
        if hasattr(self, 'template_name'):
            interface_name = self.template_name
            class_name = to_camel_case(interface_name)

        all_keys = []
        if data:
            all_keys = get_sent_keys(data) + get_meta_keys(data)
            all_keys = [_ for _ in all_keys if _ not in excluded_sent_cols]

        # Create custom init function
        def custom_init(self, **kwargs):
            for key in all_keys:
                if key not in kwargs.keys():
                    raise ValueError(f"Missing key '{key}'. Keys as defined by the '{interface_name}' interface are: {all_keys}")
            for key, value in kwargs.items():
                setattr(self, key, value)

        def __metakeys__(self) -> List[str]:
            return get_meta_keys(data)

        return type(f'{class_name}Entry', (Entry,), {"__init__": custom_init, "__metakeys__": __metakeys__})

    def create_edit_class(self, name: str) -> Edit:
        """
        Define custom edit class given a typology
        """
        class_name = to_camel_case(name)

        # Validate inputs in typology
        edit_labels = [e['name'] for e in self.edits if 'name' in e.keys()]
        if name not in edit_labels:
            raise ValueError(f"Typology does not contain edit category '{name}'. Recieved: {edit_labels}")
        edit_declaration = [e for e in self.edits if e['name'] == name]
        if len(edit_declaration) > 1:
            raise ValueError(f"Typology contains multiple edit categories with name '{name}'.")
        edit_declaration = edit_declaration[0]

        # Use typology to get edit declaration
        all_keys = []
        if 'enable_input' in edit_declaration.keys() and edit_declaration['enable_input']:
            all_keys += ['input_idx']
        if 'enable_output' in edit_declaration.keys() and edit_declaration['enable_output']:
            all_keys += ['output_idx']

        # Initialize annotation declaration
        if 'annotation' in edit_declaration.keys():
            annotation_class = self.create_annotation_class(name, edit_declaration['annotation'])
            self.annotation_classes.update({name: annotation_class})

        is_composite = 'type' in edit_declaration.keys() and edit_declaration['type'] == 'composite'
        if is_composite:
            edit_classes = self.edit_classes

        # Create custom init function
        def custom_init(self, **kwargs):
            for key in all_keys:
                if key not in kwargs.keys():
                    raise ValueError(f"Missing key '{key}'. Keys as defined by the '{name}' edit type are: {all_keys}")
            for key, value in kwargs.items():
                setattr(self, key, value)
            
            # Initialize constituent edits
            if is_composite:
                self.constituent_edits = []
                for edit in kwargs['constituent_edits']:
                    self.constituent_edits += [edit_classes[edit['category']](**edit)]

            # Initialize annotation declaration
            if 'annotation' in kwargs.keys() and kwargs['annotation'] is not None:
                self.annotation = annotation_class(**kwargs['annotation'])

        def __editname__(self) -> str:
            return name

        return type(f'{class_name}Edit', (Edit,), {"__init__": custom_init, "__editname__": __editname__})

    def create_annotation_class(self, name: str, annotation_declaration: dict) -> Annotation:
        """
        Creates a annotation class for the root question, given the dict corresponding to the annotation
        """
        class_name = to_camel_case(name)

        all_keys = [o['name'] for o in annotation_declaration if 'name' in o.keys()]
        keys_with_children = [o['name'] for o in annotation_declaration if \
            'name' in o.keys() and \
            ('options' in o.keys() and isinstance(o['options'], list))]

        child_subclasses = {child_key: {} for child_key in keys_with_children}
        for child_key in keys_with_children:
            child_declaration = [o for o in annotation_declaration if o['name'] == child_key][0]
            for child_option in child_declaration['options']:
                child_subclasses[child_key][child_option['name']] = self.create_annotation_subclass(child_option['name'], child_option)
            
        def __annotationname__(self) -> str:
            return name

        def custom_init(self, **kwargs):
            for key in all_keys:
                if key not in kwargs.keys():
                    logger.warn(f"Missing key '{key}' from annotation '{kwargs}'. Keys as defined by the '{name}' annotation type are: {all_keys}")
                    pass
            for key, value in kwargs.items():
                if key in keys_with_children:
                    passed_value = value
                    if value['val'] in value.keys() and isinstance(value[value['val']], dict): 
                        passed_value = value[value['val']]
                    setattr(self, key, child_subclasses[key][value['val']](**passed_value))
                else:
                    if isinstance(value, str) and value in value_map.keys(): value = value_map[value]
                    setattr(self, key, value)

        return type(f'{class_name}Annotation', (Annotation,), {"__init__": custom_init, "__annotationname__": __annotationname__})

    def create_annotation_subclass(self, name: str, annotation_declaration: dict) -> Annotation:
        """
        Creates a annotation class for the sub-questions. This is recursive and unlike create_annotation_class it cannot
        support multiple questions, only multiple options for a single question.
        """
        class_name = to_camel_case(name)

        has_children = 'options' in annotation_declaration.keys() and isinstance(annotation_declaration['options'], list)

        if has_children:
            keys_with_children = [o['name'] for o in annotation_declaration['options'] if \
                'name' in o.keys() and \
                ('options' in o.keys() and isinstance(o['options'], list))]
            child_subclasses = {}
            for child_key in keys_with_children:
                child_declaration = [o for o in annotation_declaration['options'] if o['name'] == child_key][0]
                child_subclasses[child_key] = self.create_annotation_subclass(child_key, child_declaration)
            
        def __annotationname__(self) -> str:
            return name

        def custom_init(self, **kwargs):
            if "val" not in kwargs.keys():
                logger.warn(f"Missing key 'val' from annotation '{kwargs}' for sub-annotation: {name}")
            key, value = kwargs["val"], kwargs["val"]
            if key in kwargs.keys(): 
                value = kwargs[kwargs["val"]]
            if has_children and key in child_subclasses:
                setattr(self, "val", child_subclasses[key](**value))
            else:
                if isinstance(value, str) and value in value_map.keys(): value = value_map[value]
                setattr(self, "val", value)

        return type(f'{class_name}', (Annotation,), {"__init__": custom_init, "__annotationname__": __annotationname__})

    def get_edit_class(self, name: str) -> Edit:
        return self.edit_classes[name]

    def get_annotation_class(self, name: str) -> Annotation:
        return self.edit_classes[name]
    
    def get_entry_class(self) -> Entry:
        if not hasattr(self, 'entry_class'):
            logger.warn("Data has not yet been loaded, so the entry class may not be fully compatible.")
        return self.entry_class
    
    def export_data(self, data: List[Entry], output_filename: str) -> None:
        """
        Export annotation data to a json file for annotation.
        """
        if len(data) < 1 or not isinstance(data[0], self.entry_class):
            raise ValueError(f"Data must be of type {self.entry_class}.")
        if not output_filename.endswith(".json"):
            raise ValueError(f"Output filename must end with '.json'. Recieved: {output_filename}")
        if os.path.dirname(output_filename) != '' and not os.path.exists(os.path.dirname(output_filename)):
            os.makedirs(os.path.dirname(output_filename))

        converted_data = self.to_dict(data)

        with open(output_filename, 'w') as f:
            json.dump(converted_data, f, indent=2)
