GLOBAL_NAMESPACE = 'global'


def parse_partial_toml(raw_text):
    """ Parses the given string for a partial implementation of TOML
    (Tom's obvious minimal language: https://github.com/toml-lang/toml).
    Partial refers to the fact that this is a very incomplete, very
    naive and unstable implementation. This function and the entire module
    should be replaced with a proper library if in any way possible.

    This implementation currently supports global and single-layer namespaces.
    All values are parsed as either strings or a list of string. Lists are
    encoded by brackets [].
    """
    items = {}
    current_section = GLOBAL_NAMESPACE

    for line in raw_text.splitlines():
        # Check (naively) what the line contains
        if len(line) > 0 and line.lstrip()[0] == '[':
            # Open a new section
            name = line.strip().strip("[]")
            current_section = name
            if current_section not in items:
                items[current_section] = {}

        elif line.find('=') >= 0:
            # We have an assignment line
            parts = line.split('=')
            assign = parts[0].strip()
            value = parts[1]

            parse_type = check_parse_type(value)
            if parse_type == 'array':
                value = parse_as_array(value)
            elif parse_type == 'string':
                value = parse_as_string(value)

            # If it's a global assignment, try to put it there, unless the space is already taken
            if current_section == GLOBAL_NAMESPACE and assign not in items:
                items[assign] = value
            elif current_section == GLOBAL_NAMESPACE:
                items[GLOBAL_NAMESPACE][assign] = value
            else:
                items[current_section][assign] = value

        else:
            # Something else, possibly a comment
            pass

    return items


def check_parse_type(raw):
    """ Checks the type for which the given value should be parsed. Currently
    only detects strings and arrays."""
    if raw.strip()[0] == '[':
        return 'array'
    else:
        return 'string'


def parse_as_string(raw):
    """ Parses the given value as string. Strips spaces, tabs, newlines, carriage
    returns, single and double quotation marks of the ends."""
    return raw.strip("\t\n\r \"'")


def parse_as_array(raw):
    """ Parses the given value as a list of string values, seperated by comma.
    Due to the shoddy implementation of this entire module, commas cannot
    appear within the string values. Strips spaces, tabs, newlines, carriage
    returns and the brackets themselves from the list value.
    See documentation of parse_as_string for further information on how the
    strings are parsed."""
    items = []
    for item in raw.strip("[]\r\n\t ").split(','):
        items.append(parse_as_string(item))
    return items


def merge_config(first, second):
    """ Given a first and second configuration, merges both together into one.
    The values in the second config replace all values with the same key in the
    same namespace of the first config. For this purpose, the global namespace
    is handled as a regular namespace."""
    new = first

    for key in first:
        if key in second:
            if isinstance(first[key], dict) and isinstance(second[key], dict):
                for sub_key in first[key]:
                    if sub_key in second[key]:
                        new[key][sub_key] = second[key][sub_key]
                for sub_key in second[key]:
                    if sub_key not in first[key]:
                        new[key][sub_key] = second[key][sub_key]
            elif isinstance(first[key], dict):
                new[key][key] = second[key]
            elif isinstance(second[key], dict):
                new[key] = second[key]
                new[key][key] = first[key]
            else:
                new[key] = second[key]

    for key in second:
        if key not in first:
            new[key] = second[key]

    return new


def write_config(config):
    """ Given a configuration, writes it as string into the (partial) toml
    format. See documentation of parse_partial_toml for what types and
    structures are supported."""
    output = ""
    for key in config:
        if isinstance(config[key], dict):
            output += "\n[" + str(key) + "]\n"
            for inner_key in config[key]:
                if isinstance(config[key][inner_key], list):
                    output += write_as_array(inner_key, config[key][inner_key])
                else:
                    output += write_as_string(inner_key, config[key][inner_key])
        elif isinstance(config[key], list):
            output += write_as_array(key, config[key])
        else:
            output += write_as_string(key, config[key])

    return output


def write_as_array(key, values):
    output = str(key) + " = [\""
    output += reduce(lambda x, y: str(x) + "\",\"" + str(y), values)
    output += "\"]\n"
    return output


def write_as_string(key, value):
    return str(key) + " = \"" + str(value) + "\"\n"