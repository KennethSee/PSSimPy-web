from typing import Callable
import inspect
import textwrap

def initialize_dict_key(dictionary: dict, key, initialization_value):
    """Initizalizes a dictionary's key-value pair with the provided initialization value if the key does not exist."""
    if key not in dictionary:
        dictionary[key] = initialization_value

def get_function_header(func: Callable, is_abstract_method:bool=True) -> str:
    """Gets the header of a given function"""
    # abstract methods will insclude "@abstractmethod" in the first row so that will need to be skipped
    header_row_num = 1 if is_abstract_method else 0
    # extract function code as text
    function_text = inspect.getsource(func)
    # extract header row and format it
    function_header = textwrap.dedent(function_text.splitlines()[header_row_num])

    return function_header