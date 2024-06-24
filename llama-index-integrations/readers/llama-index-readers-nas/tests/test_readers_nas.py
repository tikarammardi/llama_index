from llama_index.core.readers.base import BaseReader
from llama_index.readers.nas import NASReader


def test_class():
    names_of_base_classes = [b.__name__ for b in NASReader.__mro__]
    assert BaseReader.__name__ in names_of_base_classes
