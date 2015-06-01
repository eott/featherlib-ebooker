def parse_partial_toml(raw_text):
    items = {}
    for line in raw_text.splitlines():
        parts = line.split('=')
        assign = parts[0].strip()
        value = parts[1]

        parse_type = check_parse_type(value)
        if parse_type == 'array':
            value = parse_as_array(value)
        elif parse_type == 'string':
            value = parse_as_string(value)

        items[assign] = value
    return items


def check_parse_type(raw):
    if raw.strip()[0] == '[':
        return 'array'
    else:
        return 'string'


def parse_as_string(raw):
    return raw.strip("\t\n\r \"'")


def parse_as_array(raw):
    items = []
    for item in raw.strip("[]\r\n\t ").split(','):
        items.append(parse_as_string(item))
    return items


# Now, do the thing
with open("sessions/0/session.toml") as conffile:
    config = parse_partial_toml(conffile.read())
    print(config)
