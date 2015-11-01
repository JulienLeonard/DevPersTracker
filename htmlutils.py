from utils import *

def htmlrow(columns):
    result = "<tr>"
    for col in columns:
        if col == None:
            col = "None"
        if isinstance( col, ( int, long, float ) ):
            col = str(col)
        result = result + "<td>" + col  + "</td>"
    result = result + "</tr>"
    return result

def htmldivrow(columns):
    result = "<tr>"
    for (col,div) in columns:
        if col == None:
            col = "None"
        result = result + "<td>" + "<div class=\"" + div + "\">" + col  + "</div></td>"
    result = result + "</tr>"
    return result


def buttonformget(link,text,div = None):
    htmlclass = ""
    if div:
        htmlclass = " class=\"" + div + "\""
    return     "<form action=\"" + link + "\" method=\"get\"><div><input type=\"submit\"" +  htmlclass + " value=\"" + text + "\"></div></form>"

def buttonformpost(link,text, div = None):
    htmlclass = ""
    if div:
        htmlclass = " class=\"" + div + "\""
    return     "<form action=\"" + link + "\" method=\"post\"><div><input type=\"submit\"" + htmlclass + " value=\"" + text + "\"></div></form>"

def htmlrows(rows):
    result = "\n".join([htmlrow(row) for row in rows])
    return result

def htmldivrows(rows):
    result = "\n".join([htmldivrow(row) for row in rows])
    return result


def htmltable(content):
    return "<table>" + content + "</table>"

def html(tag,text):
    return "<" + tag + ">" + text + "</" + tag + ">"

def headcss():
    return """
<head>
  <link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
</head>
"""

def htmllink(url,text):
    return "<a href=\"" + url + "\">" + text + "</a>"

def htmlform(action,lines,submitlabel):
    lines = ["<div>" + line + "</div>" for line in lines]
    content = "\n".join(lines)

    return "<form action=\"" + action + "\" method=\"post\">" + content + "<div><input type=\"submit\" value=\"" + submitlabel + "\"></div></form>"

def htmltextarea(name,value,nrows = "1"):
    return "<textarea name=\"" + name + "\"         rows=\"" + nrows + "\" cols=\"40\">" + str(value) + "</textarea>"

def htmlbody(content):
    return '<html><body>' + headcss() + content + '</body></html>'

def writehtmlresponse(self,content):
    self.response.write(htmlbody("\n".join(content)))

def htmldiv(scontent):
    return "<div>" + scontent + "</div>"

def htmlcenter(lcontent):
    return ["<div align=\"center\">"] + lcontent + ["</div>"]

