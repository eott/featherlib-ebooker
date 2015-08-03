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


def create_epub_for_session(session_id):
    """Create the epub file for the session with the given id. It is assumed
    that the session config file contains the necessary data. However since a
    default config is merged with the session's data, missing data will be
    replaced with default values. Thus the function won't fail, but may
    create unexpected output."""

    config = get_config_for_session(session_id)
    session_path = "sessions/" + session_id + "/"
    epub_path = session_path + config["book"]["name"] + "/"

    # Read chapters and save chapter content in config
    chapters = []
    for chapterFilename in config["book"]["chapters"]:
        with open(session_path + chapterFilename) as chapterFile:
            output = params.apply_params(chapterFile.read(), config)
            config[chapterFilename]["content"] = output

    # Clone skeleton and parameterize static params
    if not os.path.exists(epub_path):
        os.mkdir(epub_path)
    if not os.path.exists(epub_path + "META-INF"):
        os.mkdir(epub_path + "META-INF")

    for filename in ["META-INF/container.xml", "book.ncx", "book.opf", "chapter.html", "mimetype", "styles.css"]:
        if not os.path.exists(epub_path + filename):
            with open(epub_path + filename, 'w') as currentFile:
                with open("skeleton/" + filename) as currentSkeletonFile:
                    content = currentSkeletonFile.read()
                    content = params.apply_params(content, config)
                    currentFile.write(content)
                    currentFile.close()

    # Split chapter file into seperate files
    with open(epub_path + "chapter.html") as chapterFile:
        pattern = re.compile(r'<!--startfile\s+(.*?)-->(.*?)<!--endfile-->', re.DOTALL)
        matches = pattern.finditer(chapterFile.read())

        if matches:
            for match in matches:
                filename = match.group(1)
                content = match.group(2)
                with open(epub_path + filename + ".html", 'w') as newFile:
                    newFile.write(content)
                    newFile.close()

    os.remove(epub_path + "chapter.html")

    # Zip the generated folder and name it a epub
    zipf = zipfile.ZipFile(epub_path + '.epub', 'w')
    for root, dirs, files in os.walk(epub_path):
        for file in files:
            archive_name = file
            if file == 'container.xml':
                archive_name = 'META-INF/container.xml'
            zipf.write(os.path.join(root, file), archive_name)
    zipf.close()


def load_or_create_session(id):
    """Tries to load the session config and data with the given id. If no session
    was found, creates a new one."""

    conf_path = "sessions/" + id + "/session.toml"
    if not os.path.exists(conf_path):
        os.makedirs("sessions/" + id)
        with open(conf_path, "w") as conf_file:
            conf_file.write("[book]")
            conf_file.close()

    session = dict()
    session["config"] = get_config_for_session(id)
    session["chapters"] = {}

    if "book" in session["config"] and "chapters" in session["config"]["book"]:
        i = 1
        for chapter_name in session["config"]["book"]["chapters"]:
            session["chapters"][chapter_name] = {}

            with open("sessions/" + id + "/" + chapter_name) as ch_file:
                chapter = session["chapters"][chapter_name]
                chapter["content"] = ch_file.read()

            if "title" in session["config"][chapter_name]:
                chapter["title"] = session["config"][chapter_name]["title"]
            else:
                chapter["title"] = ""

            if "nr" in session["config"][chapter_name]:
                chapter["nr"] = session["config"][chapter_name]["nr"]
            else:
                chapter["nr"] = i

            i += 1

    return session


def write_session_to_files(session_id, session):
    """ Writes the given session with the given session id to the file system.
    The session config is written to the session config file, while the chapter
    content is written to the respective chapter files."""

    # Transfer session metadata to config and write chapter content
    chapters = []
    for chapter in session["chapters"]:
        chapter_name = "ch" + str(chapter["nr"])
        chapters.append(chapter_name)
        session["config"][chapter_name] = {}
        session["config"][chapter_name]["title"] = chapter["title"]
        session["config"][chapter_name]["nr"] = chapter["nr"]

        with open("sessions/" + session_id + "/" + chapter_name, "w") as ch_file:
            ch_file.write(chapter["content"])
            ch_file.close()

    session["config"]["book"]["chapters"] = chapters

    with open("sessions/" + session_id + "/session.toml", "w") as conf_file:
        conf_file.write(pt.write_config(session["config"]))
        conf_file.close()