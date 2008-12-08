#!/usr/bin/env python

"""DocZilla: A documentation generator based on Apple documentation style.

DocZilla format:

    @ Document Title (It will be show on the <title> and <h1>)

    A short overview of the entire document. (Can use Markdown format, but
    no header is allowed. So you can write multiple paragraphs, just don't
    create new headers.)

    # Entry Name (A short entry name, like the function name)
    % AttrName: Attr Value (Attr Name can be 'in', 'sa', for "Declared In",
      "See Also" correspondingly. For "sa", you can specify a comma separ-
      ated list. For "in", it will be treated as a string. More than one
      attributes are allowed.)

    A short, one line synopsis, in Markdown format.

        type func(params) (The function prototype, can be more than one
                           line, but each line must be started with four
                           spaces)

    A longer, multi-line discussion, on the usage and return value. In
    Markdown format.
"""

import os, sys, markdown2, tenjin
from tenjin.helpers import *

(GET_TITLE, GET_OVERVIEW, GET_NAME, GET_ATTR, GET_SYNOPSIS, GET_FUNC, GET_DISCUSSION) = range(7)

engine      = tenjin.Engine(encoding="utf-8")
markdowner  = markdown2.Markdown()
title       = ""
overview    = ""
fin         = sys.stdin
fout        = sys.stdout
state       = GET_TITLE
entry       = {}
entries     = []

for line in fin:
    if state == GET_TITLE:
        if line[0] == "@":
            title = line[1:].strip()
            state = GET_OVERVIEW

    elif state == GET_OVERVIEW:
        if line[0] == "#":
            overview = markdowner.convert(overview)
            entry["name"] = line[1:].strip()
            state = GET_ATTR
        else:
            overview += line

    elif state == GET_NAME:
        if line[0] == "#":
            entry["name"] = line[1:].strip()
            state = GET_ATTR

    elif state == GET_ATTR:
        if line[0] == "%":
            keylen = line.find(":")
            key = line[1:keylen].strip()
            entry[key] = line[keylen + 1:].strip()
            if key == "sa":
                entry[key] = [ item.strip() for item in entry[key].split(",")]
        else:
            state = GET_SYNOPSIS

    elif state == GET_SYNOPSIS:
        entry["synopsis"] = markdowner.convert(line.strip())
        state = GET_FUNC
        entry["func"] = ""

    elif state == GET_FUNC:
        if len(entry["func"]) == 0 and line == "\n":
            continue

        if line[0:4] == "    ":
            entry["func"] += line[4:].strip()

        else:
            entry["discussion"] = line.strip()
            state = GET_DISCUSSION

    elif state == GET_DISCUSSION:
        if line == "\n":
            entry["discussion"] = markdowner.convert(entry["discussion"])
            entries.append(entry)

            entry = {}
            state = GET_NAME
        else:
            entry["discussion"] += (len(entry["discussion"]) and " " or "") + line.strip()

    else:
        print("You shouldn't be here (state %d)." % state)

if entry:
    if entry["discussion"]:
        entry["discussion"] = markdowner.convert(entry["discussion"])
    entries.append(entry)

context = { "title": title, "overview": overview, "entries": entries }
fout.write(engine.render("%s/template.pyhtml" % sys.path[0], context).encode("utf-8"))

if not os.path.isfile("style.css"):
    os.system("cp -f %s/style.css style.css" % sys.path[0])

