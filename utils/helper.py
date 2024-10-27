from typing import Callable
import inspect
import textwrap
import re
import ast
from collections import OrderedDict

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


def replace_whitespace_with_underscore(input_string):
    """
    Replaces all whitespace characters in the input string with underscores.
    
    Args:
        input_string (str): The input string to process.
        
    Returns:
        str: The modified string with underscores instead of whitespaces.
    """
    return input_string.replace(" ", "_")


class ClassImplementationModifier():

    def __init__(self, code: str):
        self.code = code

    def replace_class_name(self, new_class_name: str):
        # Regular expression to match the class name in the class definition
        pattern = r"^class\s+\w+\s*(\(.*\))?:"

        # Replace the class definition with the new class signature
        modified_code = re.sub(
            pattern,
            f"class {new_class_name}:",
            self.code,
            count=1,
            flags=re.MULTILINE
        )
        
        self.code = modified_code

    @staticmethod
    def extract_function_code(code: str, function_name: str) -> str:
        """
        Extracts the full chunk of code for a given function name,
        including decorators like @staticmethod or @abstractmethod.

        Args:
            code (str): The complete code as a string.
            function_name (str): The name of the function to extract.

        Returns:
            str: The full code of the specified function, or an empty string if not found.
        """
        # Parse the code into an AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in code: {e}")

        # Initialize variables
        function_node = None

        # Find the function definition node
        class NodeVisitor(ast.NodeVisitor):
            def __init__(self):
                self.function_node = None

            def visit_FunctionDef(self, node):
                if node.name == function_name:
                    self.function_node = node
                # Continue walking to find nested functions if needed
                self.generic_visit(node)

        visitor = NodeVisitor()
        visitor.visit(tree)
        function_node = visitor.function_node

        if not function_node:
            return ""

        # Get the lines corresponding to the function definition
        code_lines = code.splitlines()
        # Adjust line numbers because ast uses 1-based indexing
        start_lineno = function_node.lineno - 1

        # For Python 3.8 and above, end_lineno is available
        if hasattr(function_node, 'end_lineno'):
            end_lineno = function_node.end_lineno
        else:
            # Estimate end_lineno by traversing the function body
            # This might not be accurate for complex functions
            end_lineno = function_node.body[-1].lineno

        # Include decorators if any
        decorator_lines = []
        for decorator in function_node.decorator_list:
            # Decorators may span multiple lines
            decorator_start = decorator.lineno - 1
            decorator_end = decorator.end_lineno if hasattr(decorator, 'end_lineno') else decorator.lineno
            decorator_lines.extend(code_lines[decorator_start:decorator_end])

        # Extract function code lines
        function_code_lines = code_lines[start_lineno:end_lineno]
        full_function_code_lines = decorator_lines + function_code_lines
        full_function_code = "\n".join(full_function_code_lines)

        return full_function_code

    def replace_function(self, function_name: str, new_function_code: str):
        # Extract the existing function code
        old_function_code = self.extract_function_code(self.code, function_name)

        if not old_function_code:
            raise ValueError(f"Function '{function_name}' not found in the provided code.")

        # Extract the leading whitespace (indentation) from the old function code
        match = re.match(r"(\s*)def", old_function_code)
        if not match:
            # Try to match decorator indentation
            match = re.match(r"(\s*)@", old_function_code)
            if not match:
                raise ValueError(f"Could not extract indentation from function '{function_name}'.")

        leading_whitespace = match.group(1)

        # Add indentation to the new function code
        indented_new_code = "\n".join(
            leading_whitespace + line if line.strip() else ""
            for line in new_function_code.splitlines()
        )

        # Ensure there is a new line before and after the new code
        formatted_new_code = f"\n{indented_new_code}\n"

        # Replace the old function code with the new one
        self.code = self.code.replace(old_function_code, formatted_new_code, 1)

    def insert_import_statement(self, import_statement: str):
        self.code = f"{import_statement}\n\n{self.code}"

    @staticmethod
    def extract_init_params(class_code: str) -> dict:
        """
        Extracts the parameters of the __init__ method from a class definition.

        Args:
            class_code (str): The class code as a string.

        Returns:
            dict: A dictionary with parameter names as keys and default values as values.
                If a parameter has no default value, its value in the dictionary is None.
        """
        # Parse the code into an AST
        try:
            tree = ast.parse(class_code)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in code: {e}")

        # Initialize variables
        init_func = None

        # Find the class definition node
        class_def = None
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_def = node
                break

        if not class_def:
            raise ValueError("No class definition found in the code.")

        # Within the class, find the __init__ method
        for node in class_def.body:
            if isinstance(node, ast.FunctionDef) and node.name == '__init__':
                init_func = node
                break

        if not init_func:
            raise ValueError("No __init__ method found in the class.")

        # Now, extract the arguments
        args = init_func.args

        # args.args is a list of ast.arg objects
        # args.defaults is a list of default values, aligned to the last N arguments
        # where N is len(defaults)
        param_names = [arg.arg for arg in args.args]
        defaults = args.defaults  # These are AST nodes representing default values

        # Exclude "self" parameter
        if param_names[0] == 'self':
            param_names = param_names[1:]
        else:
            raise ValueError("__init__ method does not have 'self' as the first parameter.")

        num_params = len(param_names)
        num_defaults = len(defaults)
        num_non_defaults = num_params - num_defaults

        # Prepare the result dictionary
        params = {}

        # Assign None to parameters without defaults
        for name in param_names[:num_non_defaults]:
            params[name] = None

        # For parameters with defaults, get the default value
        for name, default in zip(param_names[num_non_defaults:], defaults):
            # default is an AST node, we need to evaluate it
            try:
                # For safety, we can use ast.literal_eval, which supports simple constants
                default_value = ast.literal_eval(default)
            except (ValueError, SyntaxError):
                # If we cannot evaluate the default value, set it to None
                default_value = None
            params[name] = default_value

        return params

    @staticmethod
    def generate_init_method(params: dict, is_inherited: bool = False , inherited_abstract_class_name: str=None) -> str:
        """
        Generates an __init__ method dynamically with given parameters.

        Args:
            params (dict): A dictionary where keys are parameter names, 
                        and values are their default values (if any).
            is_inherited (bool): If True, adds `super().__init__()` to the code.

        Returns:
            str: The generated __init__ method as a string.
        """
        last_comma_string = ", " if len(params) > 0 else ""
        if inherited_abstract_class_name is None:
            inherited_abstract_class_name = "super()"
            init_arg = ""
        else:
            init_arg = "self"
        # Separate parameters with and without default values
        required_params = [k for k, v in params.items() if v is None]
        optional_params = [f"{k}={repr(v)}" for k, v in params.items() if v is not None]

        # Combine required and optional parameters into a parameter list
        all_params = ", ".join(required_params + optional_params)

        # Generate the body of the __init__ method
        body_lines = []
        if is_inherited:
            body_lines.append(f"{inherited_abstract_class_name}.__init__({init_arg})")  # Add super().__init__() if inherited

        # Add assignments for all parameters
        for param in params.keys():
            body_lines.append(f"self.{param} = {param}")

        # Join the body lines with proper indentation
        body = "\n    ".join(body_lines)

        # Generate the final __init__ method
        init_method = f"def __init__(self{last_comma_string}{all_params}):\n    {body}"
        return init_method