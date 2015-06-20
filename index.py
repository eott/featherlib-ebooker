#!/usr/bin/python

import cgi
import Cookie


cookie = Cookie.SimpleCookie()
cookie['session_id'] = 'daosjdniwludbniwluadwad'
cookie['session_id']['expires'] = 24 * 60 * 60

print cookie
print """Content-type: text/html

<html>

<head><title>Sample CGI Script</title></head>

<body>

<h3> Sample CGI Script </h3>
"""

form = cgi.FieldStorage()
message = form.getvalue("message", "(no message)")

print """

<p>Previous message: %s</p>

<p>form

<form method="post" action="main.py">
<p>message: <input type="text" name="message"/></p>
</form>

</body>

</html>
""" % cgi.escape(message)