#!/usr/bin/python

import cgi
import Cookie


cookie = Cookie.SimpleCookie()
cookie['session_id'] = 'daosjdniwludbniwluadwad'
cookie['session_id']['expires'] = 24 * 60 * 60

#form = cgi.FieldStorage()
#message = form.getvalue("message", "(no message)")

print cookie
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

        <div class="chapter">
            <label for="chapter-1">Chapter 1</label><br/>
            <input type="text" name="chapter-1-name" id="chapter-1-name"/><br/>
            <textarea name="chapter-1-content" id="chapter-1-content"></textarea>
        </div>

        <button class="addChapter" onClick="addChapter()">Add chapter</button><br/>

        <button type="submit" name="save" id="save">Save</button>
        <button type="submit" name="create" id="create">Create epub</button>
    </form>

</body>
</html>
"""