from abc import ABC, abstractmethod


class Entry:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        attributes = ", ".join(f"\n  {k} = {v}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attributes}\n)"

    def __repr__(self):
        return self.__str__()

# class Interface(ABC):
#     @abstractmethod
#     def load_data(self, path):
#         pass

#     @abstractmethod
#     def save_data(self, path):
#         pass

#     @abstractmethod
#     def add_example(self, example):
#         pass

#     @abstractmethod
#     def get_examples(self):
#         pass

#     @abstractmethod
#     def add_annotation(self, example_id, annotation):
#         pass

#     @abstractmethod
#     def get_annotations(self, example_id):
#         pass

# class Example:
#     def __init__(self, example_id, text, metadata=None):
#         self.example_id = example_id
#         self.text = text
#         self.metadata = metadata if metadata else {}
#         self.annotations = []

#     def add_annotation(self, annotation):
#         self.annotations.append(annotation)

#     def get_annotations(self):
#         return self.annotations

#     # Other methods specific to Example class can be added here

# class Edit:
#     def __init__(self, edit_type, edited_text, start_idx, end_idx):
#         self.edit_type = edit_type
#         self.edited_text = edited_text
#         self.start_idx = start_idx
#         self.end_idx = end_idx

#     # Other methods specific to Edit class can be added here

# # class Annotation:
#     # Other methods specific to Annotation class can be added here