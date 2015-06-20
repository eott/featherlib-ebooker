import re
from partial_toml import GLOBAL_NAMESPACE


def apply_params(raw_text, config):
    """ Given a string and a configuration, searches the text for parameter
    references and replaces all parameters with their values, if they
    exist within the referenced namespace in the config. Supports static
    and iterated parameters:

    Static:
        "I am an example and I'm using a parameter called bar in the name-
        space foo. Here's its value: <%foo.bar%>"

    Iterated:
        "I am an example and I'm using an iterated parameter to list all
        prime numbers and their squares less than 10:
        <%+primes%>
        <%~number%>: <%~square%>
        <%-primes%>
        "

        The way iterated parameters work is, that they expect to be given a list
        of strings, where each string is an existing namespace within the config.
        They then replace the unit between the + and - tags with the unit, where
        the unit is parameterized with the values of the corresponding namespace.
        In the example above, if primes is the list ["2", "3", "5", "7"], then
        the config should have the namespaces 2, 3, 5 and 7 where each namespace
        contains the parameters number and square with the actual values for
        each number.
    """
    text = raw_text

    # First, replace the static params
    replacements = {}
    pattern = re.compile('<%[^-+~].*?%>')
    matches = pattern.findall(text)

    for match in matches:
        parts = match.strip().strip('<>%').split('.')
        if len(parts) == 1:
            key = parts[0]
            if key in config:
                replacements[match] = config[key]
            elif GLOBAL_NAMESPACE in config and key in config[GLOBAL_NAMESPACE]:
                replacements[match] = config[GLOBAL_NAMESPACE][key]
        elif len(parts) == 2:
            ns = parts[0]
            key = parts[1]
            if ns in config and key in config[ns]:
                replacements[match] = config[ns][key]
        else:
            # Nested namespaces not supported yet
            pass

    for old in replacements:
        text = text.replace(old, replacements[old])

    # Second, replace iterated params
    pattern = re.compile(r'<%\+(.*?)%>(.*?)(<%-\1%>)', re.DOTALL)
    matches = pattern.finditer(text)
    replacements = []

    if matches:
        for match in matches:
            parts = match.group(1).split('.')
            units = []
            if len(parts) == 1:
                key = parts[0]
                if key in config:
                    units = config[key]
                elif GLOBAL_NAMESPACE in config and key in config[GLOBAL_NAMESPACE]:
                    units = config[GLOBAL_NAMESPACE][key]
            elif len(parts) == 2:
                ns = parts[0]
                key = parts[1]
                if ns in config and key in config[ns]:
                    units = config[ns][key]

            tmp = ""
            for unit in units:
                params = config[unit]
                unit_text = match.group(2)
                for param_key in params:
                    unit_text = unit_text.replace('<%~' + param_key + '%>', params[param_key])
                tmp += unit_text
            replacements.append({
                "old": match.group(0),
                "new": tmp,
            })
        for repl in replacements:
            text = text.replace(repl["old"], repl["new"])

    return text