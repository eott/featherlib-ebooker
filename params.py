import re
from partial_toml import GLOBAL_NAMESPACE


def apply_params(raw_text, config):
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