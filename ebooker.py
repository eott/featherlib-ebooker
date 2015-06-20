import re
import os
import zipfile
import partial_toml as pt
import params


def get_config_for_session(id):
    """ Reads the configuration file for the session with the given id, parses
    it, merges it with a default configuration and returns the generated configuration
    file. The session config will overwrite the parameters of the default config."""
    with open("sessions/" + id + "/session.toml") as conf_file:
        config_session = pt.parse_partial_toml(conf_file.read())
        with open("default_params.toml") as def_conf_file:
            config_default = pt.parse_partial_toml(def_conf_file.read())
            config = pt.merge_config(config_default, config_session)
            return config


# Now, do the thing
config = get_config_for_session("0")

# Read chapters and save chapter content in config
chapters = []
for chapterFilename in config["book"]["chapters"]:
    with open("sessions/0/" + chapterFilename) as chapterFile:
        output = params.apply_params(chapterFile.read(), config)
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
                content = params.apply_params(content, config)
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