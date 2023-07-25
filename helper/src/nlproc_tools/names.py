from abc import ABC, abstractmethod

class Interface(ABC):
    @abstractmethod
    def load_data(self, path):
        pass

    @abstractmethod
    def save_data(self, path):
        pass

    @abstractmethod
    def add_example(self, example):
        pass

    @abstractmethod
    def get_examples(self):
        pass

    @abstractmethod
    def add_annotation(self, example_id, annotation):
        pass

    @abstractmethod
    def get_annotations(self, example_id):
        pass

class Example:
    def __init__(self, example_id, text, metadata=None):
        self.example_id = example_id
        self.text = text
        self.metadata = metadata if metadata else {}
        self.annotations = []

    def add_annotation(self, annotation):
        self.annotations.append(annotation)

    def get_annotations(self):
        return self.annotations

    # Other methods specific to Example class can be added here

class Edit:
    def __init__(self, edit_type, edited_text, start_idx, end_idx):
        self.edit_type = edit_type
        self.edited_text = edited_text
        self.start_idx = start_idx
        self.end_idx = end_idx

    # Other methods specific to Edit class can be added here

class Annotation:
    def __init__(self, annotation_id, annotated_text, annotation_type, category=None):
        self.annotation_id = annotation_id
        self.annotated_text = annotated_text
        self.annotation_type = annotation_type
        self.category = category

    # Other methods specific to Annotation class can be added here
