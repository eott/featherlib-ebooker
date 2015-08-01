#!/usr/bin/python

import cgi
import Cookie
import uuid
import os
import ebooker


def get_chapter_html(nr, content):
    html = """

        <div class="chapter" id="chapter-%(nr)s">
            <label for="chapter-%(nr)s">Chapter %(nr)s</label><br/>
            <input type="text" name="chapter-%(nr)s-name" id="chapter-%(nr)s-name"/><br/>
            <textarea name="chapter-%(nr)s-content" id="chapter-%(nr)s-content">%(content)s</textarea>
        </div>
    """ % {'nr': nr, 'content': content}
    return html


cookie_data = {}

if 'HTTP_COOKIE' in os.environ:
    cookies = os.environ['HTTP_COOKIE']
    cookies = cookies.split('; ')

    for cookie in cookies:
        cookie = cookie.split('=')
        cookie_data[cookie[0]] = cookie[1]

if "session_id" not in cookie_data:
    session_id = str(uuid.uuid4())
    cookie = Cookie.SimpleCookie()
    cookie['session_id'] = session_id
    cookie['session_id']['expires'] = 24 * 60 * 60
    print cookie
else:
    session_id = cookie_data["session_id"]

session = ebooker.load_or_create_session(session_id)

#form = cgi.FieldStorage()
#message = form.getvalue("message", "(no message)")

print """Content-type: text/html"""
print
print """
<!DOCTYPE html>
<html>
<head>
    <title>featherlib ebooker</title>
    <meta charset="utf-8"/>
    <link rel="icon" type="image/png" href="favicon.png"/>
    <link href="styles/default-style.css" rel="stylesheet" type="text/css"/>
</head>

<body>
    <h1>featherlib ebooker</h1>
    <h2>Make epubs in one simple form.</h2>

    <p>
        Here's how:
        <ol>
            <li>Add title, author and optionally additional information about the document</li>
            <li>Paste the text for each chapter into the chapter input fields</li>
            <li>Click <i>Make epub</i>, then wait for the file dialog to save your epub</li>
        </ol>
    </p>

    <form id="docForm" method="post" action="index.py">
        <label for="doc-name">Document name</label><br/>
        <input type="text" name="doc-name" id="doc-name"/><br/>

        <label for="doc-author">Author</label><br/>
        <input type="text" name="doc-author" id="doc-author"/><br/>

        <span onClick="showAdditionalDocFields()">Expand</span>
        <div id="additionalDocFields" style="display: none;">
            <label for="doc-css">CSS</label><br/>
            <input type="text" name="doc-css" id="doc-css"/><br/>
        </div>

"""

print get_chapter_html(1, "")

print """

        <div id="chapterInsertMarker"></div>
        <span class="addChapter" onClick="addChapter()">Add chapter</span><br/>

        <button type="submit" name="save" id="save">Save</button>
        <button type="submit" name="create" id="create">Create epub</button>

        <input type="hidden" name="no-of-chapters" id="no-of-chapters" value="1"/>
    </form>

    <script type="text/javascript">
        function addChapter(event) {
            var element = document.getElementById("no-of-chapters");
            var no = parseInt(element.value) + 1;
            element.value = no;

            var chapterWrapper = document.createElement("div");

            var chapterLabel = document.createElement("label");
            chapterLabel.setAttribute("for", "chapter-" + no);
            chapterLabel.textContent = "Chapter " + no;

            var chapterInput = document.createElement("input");
            chapterInput.setAttribute("type", "text");
            chapterInput.setAttribute("name", "chapter-" + no + "-name");
            chapterInput.setAttribute("id", "chapter-" + no + "-name");

            var chapterTextArea = document.createElement("textarea");
            chapterTextArea.setAttribute("name", "chapter-" + no + "-content");
            chapterTextArea.setAttribute("id", "chapter-" + no + "-content");

            chapterWrapper.appendChild(chapterLabel);
            chapterWrapper.appendChild(document.createElement("br"));
            chapterWrapper.appendChild(chapterInput);
            chapterWrapper.appendChild(document.createElement("br"));
            chapterWrapper.appendChild(chapterTextArea);

            var marker = document.getElementById("chapterInsertMarker");
            document.getElementById("docForm").insertBefore(chapterWrapper, marker);
        }

        function showAdditionalDocFields() {
            element = document.getElementById("additionalDocFields");
            element.setAttribute("style", "display: block;");
        }
    </script>

</body>
</html>
"""