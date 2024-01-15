#!/bin/python3

import os

files = os.listdir("posts/")
files.sort(reverse=True)
fp = open("posts.json", 'w')
fp.write("{\"posts\":[")
for f in files:
    if f == "undefined.md" or f == "about.md":
        continue
    url = f[:-3]
    date = f[:4] + "-" + f[4:6] + "-" + f[6:8]
    title = f[10:-3].replace("_", " ")
    fp.write("{\"url\":\"" + url + "\",\"date\":\"" + date + "\",\"title\":\"" + title + "\"},")
fp.write("]}")
fp.close()
