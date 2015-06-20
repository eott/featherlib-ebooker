import re
import os
import zipfile

GLOBAL_NAMESPACE = 'global'


def parse_partial_toml(raw_text):
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


def merge_config(first, second):
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


def get_config_for_session(id):
    with open("sessions/" + id + "/session.toml") as conf_file:
        config_session = parse_partial_toml(conf_file.read())
        with open("default_params.toml") as def_conf_file:
            config_default = parse_partial_toml(def_conf_file.read())
            config = merge_config(config_default, config_session)
            return config


# Now, do the thing
config = get_config_for_session("0")

# Read chapters and save chapter content in config
chapters = []
for chapterFilename in config["book"]["chapters"]:
    with open("sessions/0/" + chapterFilename) as chapterFile:
        output = apply_params(chapterFile.read(), config)
        config[chapterFilename]["content"] = output

# Clone skeleton and parameterize static params
if not os.path.exists("sessions/0/" + config["book"]["name"]):
    os.mkdir("sessions/0/" + config["book"]["name"])
if not os.path.exists("sessions/0/" + config["book"]["name"] + "/META-INF"):
    os.mkdir("sessions/0/" + config["book"]["name"] + "/META-INF")

for filename in ["META-INF/container.xml", "book.ncx", "book.opf", "chapter.html", "mimetype", "styles.css"]:
    if not os.path.exists("sessions/0/" + config["book"]["name"] + "/" + filename):
        with open("sessions/0/" + config["book"]["name"] + "/" + filename, 'w') as currentFile:
            with open("skeleton/" + filename) as currentSkeletonFile:
                content = currentSkeletonFile.read()
                content = apply_params(content, config)
                currentFile.write(content)
                currentFile.close()

# Split chapter file into seperate files
with open("sessions/0/" + config["book"]["name"] + "/" + "chapter.html") as chapterFile:
    pattern = re.compile(r'<!--startfile\s+(.*?)-->(.*?)<!--endfile-->', re.DOTALL)
    matches = pattern.finditer(chapterFile.read())

    if matches:
        for match in matches:
            filename = match.group(1)
            content = match.group(2)
            with open("sessions/0/" + config["book"]["name"] + "/" + filename + ".html", 'w') as newFile:
                newFile.write(content)
                newFile.close()

os.remove("sessions/0/" + config["book"]["name"] + "/chapter.html")

# Zip the generated folder and name it a epub
zipf = zipfile.ZipFile("sessions/0/" + config["book"]["name"] + '.epub', 'w')
for root, dirs, files in os.walk("sessions/0/" + config["book"]["name"]):
    for file in files:
        archive_name = file
        if file == 'container.xml':
            archive_name = 'META-INF/container.xml'
        zipf.write(os.path.join(root, file), archive_name)
zipf.close()