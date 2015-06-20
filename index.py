#!/usr/bin/python

import cgi
import Cookie


cookie = Cookie.SimpleCookie()
cookie['session_id'] = 'daosjdniwludbniwluadwad'
cookie['session_id']['expires'] = 24 * 60 * 60

headers = """Content-type: text/html

"""

#form = cgi.FieldStorage()
#message = form.getvalue("message", "(no message)")

print cookie
print headers
print
"""<html>
<head>
    <title>featherlib ebooker</title>
</head>

<body>
    <h3> featherlib ebooker </h3>

    <p>Make epub with a simple form.</p>

</body>
</html>
"""