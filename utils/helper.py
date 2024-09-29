from typing import Callable
import inspect
import textwrap

def initialize_dict_key(dictionary: dict, key, initialization_value):
    """Initizalizes a dictionary's key-value pair with the provided initialization value if the key does not exist."""
    if key not in dictionary:
        dictionary[key] = initialization_value

def get_function_header(func: Callable, is_abstract_method:bool=True, is_static_method:bool=False) -> str:
    """Gets the header of a given function"""
    # abstract methods will insclude "@abstractmethod" in the first row so that will need to be skipped
    # likewise with staticmethods
    header_row_num = 0
    if is_abstract_method:
        header_row_num += 1
    if is_static_method:
        header_row_num += 1
    # extract function code as text
    function_text = inspect.getsource(func)
    # extract header row and format it
    function_header = textwrap.dedent(function_text.splitlines()[header_row_num])

    return function_header