#!/usr/bin/env python

"""DocZilla: A documentation generator based on Apple documentation style."""

import os, sys, markdown2, tenjin
from tenjin.helpers import *

(GET_TITLE, GET_OVERVIEW, GET_NAME, GET_ATTR, GET_FUNC, GET_DESC) = range(6)

engine      = tenjin.Engine()
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

        if line[0:4] == "    ":
            entry["func"] = line[4:].strip()
            state = GET_FUNC

    elif state == GET_FUNC:
        if line[0:4] == "    ":
            entry["func"] += " " + line[4:].strip()

        else:
            entry["desc"] = line.strip()
            state = GET_DESC

    elif state == GET_DESC:
        if line == "\n":
            entry["desc"] = markdowner.convert(entry["desc"])
            entries.append(entry)

            entry = {}
            state = GET_NAME
        else:
            entry["desc"] += (len(entry["desc"]) and " " or "") + line.strip()

    else:
        print("You shouldn't be here (state %d)." % state)

if entry:
    if entry["desc"]:
        entry["desc"] = markdowner.convert(entry["desc"])
    entries.append(entry)

context = { "title": title, "overview": overview, "entries": entries }
fout.write(engine.render("%s/template.pyhtml" % sys.path[0], context))

if not os.path.isfile("style.css"):
    os.system("cp -f %s/style.css style.css" % sys.path[0])

