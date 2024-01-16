import os

filelist = []
for path, subdirs, files in os.walk("posts/"):
    for name in files:
        if name[-3:] == ".md":
            f = os.path.join(path, name)
            filelist.append(f[6:-3])
filelist.sort(reverse=True)
fp = open("posts.json", 'w')
fp.write("{\"posts\":[")
for f in filelist:
    if f == "undefined" or f == "about":
        continue
    fn = f.replace(os.path.sep, "")
    url = f
    date = fn[:4] + "-" + fn[4:6] + "-" + fn[6:8]
    title = fn[10:].replace("_", " ")
    fp.write("{\"url\":\"" + url + "\",\"date\":\"" + date + "\",\"title\":\"" + title + "\"},")
fp.write("]}")
fp.close()
