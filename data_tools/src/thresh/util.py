from typing import List
import logging, os

def verify_exists(data_path: str) -> None:
    if not os.path.isfile(data_path):
        raise ValueError(f"The provided path does not point to an existing file. Recieved: '{data_path}'")


def to_camel_case(string: str) -> str:
    words = string.split('_')
    return ''.join(word.capitalize() for word in words)


def get_sent_keys(data: dict) -> List[str]:
    """
    Get all unique keys in entries
    """
    return list(set([_ for _ in [list(s.keys()) for s in data] for _ in _]))


def get_meta_keys(data: dict) -> List[str]:
    """
    Get all unique metadata keys
    """
    return list(set([_ for _ in [list(s['metadata'].keys()) for s in data if 'metadata' in s.keys()] for _ in _]))


def format_class_str(class_str: any) -> str:
    """
    Indents any class string for pretty printing
    """
    return str(class_str).replace('\n', '\n  ')
