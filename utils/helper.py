def initialize_dict_key(dictionary: dict, key, initialization_value):
    """Initizalizes a dictionary's key-value pair with the provided initialization value if the key does not exist."""
    if key not in dictionary:
        dictionary[key] = initialization_value