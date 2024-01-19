import os

filelist = []
for path, subdirs, files in os.walk("posts/"):
    for name in files:
        if name == "undefined.md" or name == "about.md":
            continue
        if name[-3:] == ".md":
            f = os.path.join(path, name)
            filelist.append(f[6:-3])
filelist.sort(reverse=True)
fp = open("posts.json", 'w')
fp.write("{\n\t\"posts\":[\n")
for f in filelist:
    fn = f.replace(os.path.sep, "")
    url = f
    date = fn[:4] + "-" + fn[4:6] + "-" + fn[6:8]
    title = fn[10:].replace("_", " ")
    fp.write("\t\t{\"url\":\"" + url + "\",\"date\":\"" + date + "\",\"title\":\"" + title + "\"}")
    if filelist.index(f) < (len(filelist) - 1):
        fp.write(",")
    fp.write("\n")
fp.write("\t]\n}\n")
fp.close()
