import os

TITLE = "Kyle's Blog"
rfp = open("template/header.template", 'r')
HEADER = rfp.read()
rfp.close()
rfp = open("template/footer.template", 'r')
FOOTER = rfp.read()
rfp.close()

def get_lastline(file):
  f = open("posts/" + file + ".md", 'rb')
  try:  # catch OSError in case of a one line file
    f.seek(-2, os.SEEK_END)
    found_content = False
    while True:
      c = f.read(1)
      if not c.isspace():
        found_content = True
      if found_content and c == b'\n':
        if found_content:
          break
      f.seek(-2, os.SEEK_CUR)
  except OSError:
    f.seek(0)
  return f.readline().decode()

def get_tags(file):
  line = get_lastline(file).strip()
  if len(line) <= 6 or line[0:6] != "Tags: ":
    return "[]"
  tags = line[6:].replace(" ", "").split(",")
  ret = "["
  for t in tags:
    ret += "\"" + t + "\""
    if t != tags[-1]:
      ret += ","
  ret += "]"
  return ret

filelist = []
for path, subdirs, files in os.walk("posts/"):
  for name in files:
    if name == "about.md":
      continue
    if name[-3:] == ".md":
      f = os.path.join(path, name)
      filelist.append(f[6:-3])
filelist.sort(reverse=True)

# make index.html
rfp = open("template/list.template", 'r')
LIST_TEMPLATE = rfp.read()
rfp.close()
LIST_TEMPLATE = LIST_TEMPLATE.replace("[[HEADER]]", HEADER)
LIST_TEMPLATE = LIST_TEMPLATE.replace("[[FOOTER]]", FOOTER)
LIST_TEMPLATE = LIST_TEMPLATE.replace("[[TITLE]]", TITLE)
LIST = "{\n\t\"posts\":[\n"
for f in filelist:
  fn = f.replace(os.path.sep, "")
  url = f.replace("%", "%25")
  url = url.replace("#", "%23")
  url = url.replace("$", "%24")
  url = url.replace("&", "%26")
  url = url.replace("+", "%2B")
  url = url.replace("-", "%2D")
  url = url.replace("?", "%3F")
  url = url.replace("@", "%40")
  date = fn[:4] + "-" + fn[4:6] + "-" + fn[6:8]
  title = fn[10:].replace("_", " ")
  LIST += "{\"url\":\"" + url + "\",\"date\":\"" + date + "\",\"title\":\"" + title + "\"}"
  if filelist.index(f) < (len(filelist) - 1):
    LIST += ","
  LIST += "\n"
LIST += "\t]\n}\n"
LIST_TEMPLATE = LIST_TEMPLATE.replace("[[DATA]]", LIST)
wfp = open("index.html", 'w')
wfp.write(LIST_TEMPLATE)
wfp.close()

# processing each file
rfp = open("template/post.template", 'r')
POST_TEMPLATE = rfp.read()
rfp.close()
POST_TEMPLATE = POST_TEMPLATE.replace("[[HEADER]]", HEADER)
POST_TEMPLATE = POST_TEMPLATE.replace("[[FOOTER]]", FOOTER)
POST_TEMPLATE = POST_TEMPLATE.replace("[[TITLE]]", TITLE)
for f in filelist:
  rfp = open("posts/" + f + ".md", 'r')
  POST = rfp.read()
  rfp.close()
  POST = POST_TEMPLATE.replace("[[DATA]]", POST)
  wfp = open("posts/" + f + ".html", 'w')
  wfp.write(POST)
  wfp.close()

# make archive.html
rfp = open("template/archive.template", 'r')
ARCHIVE_TEMPLATE = rfp.read()
rfp.close()
ARCHIVE_TEMPLATE = ARCHIVE_TEMPLATE.replace("[[HEADER]]", HEADER)
ARCHIVE_TEMPLATE = ARCHIVE_TEMPLATE.replace("[[FOOTER]]", FOOTER)
ARCHIVE_TEMPLATE = ARCHIVE_TEMPLATE.replace("[[TITLE]]", TITLE)
LIST = "{\n\t\"posts\":[\n"
for f in filelist:
  fn = f.replace(os.path.sep, "")
  url = f.replace("%", "%25")
  url = url.replace("#", "%23")
  url = url.replace("$", "%24")
  url = url.replace("&", "%26")
  url = url.replace("+", "%2B")
  url = url.replace("-", "%2D")
  url = url.replace("?", "%3F")
  url = url.replace("@", "%40")
  date = fn[:4] + "-" + fn[4:6] + "-" + fn[6:8]
  title = fn[10:].replace("_", " ")
  LIST += "{\"url\":\"" + url + "\",\"date\":\"" + date + "\",\"title\":\"" + title + "\"}"
  if filelist.index(f) < (len(filelist) - 1):
    LIST += ","
  LIST += "\n"
LIST += "\t]\n}\n"
ARCHIVE_TEMPLATE = ARCHIVE_TEMPLATE.replace("[[DATA]]", LIST)
wfp = open("archive.html", 'w')
wfp.write(ARCHIVE_TEMPLATE)
wfp.close()

# make tags.html
rfp = open("template/tags.template", 'r')
TAGS_TEMPLATE = rfp.read()
rfp.close()
TAGS_TEMPLATE = TAGS_TEMPLATE.replace("[[HEADER]]", HEADER)
TAGS_TEMPLATE = TAGS_TEMPLATE.replace("[[FOOTER]]", FOOTER)
TAGS_TEMPLATE = TAGS_TEMPLATE.replace("[[TITLE]]", TITLE)
LIST = "{\n\t\"posts\":[\n"
for f in filelist:
  fn = f.replace(os.path.sep, "")
  url = f.replace("%", "%25")
  url = url.replace("#", "%23")
  url = url.replace("$", "%24")
  url = url.replace("&", "%26")
  url = url.replace("+", "%2B")
  url = url.replace("-", "%2D")
  url = url.replace("?", "%3F")
  url = url.replace("@", "%40")
  date = fn[:4] + "-" + fn[4:6] + "-" + fn[6:8]
  title = fn[10:].replace("_", " ")
  tags = get_tags(f)
  LIST += "{\"url\":\"" + url + "\",\"date\":\"" + date + "\",\"title\":\"" + title + "\",\"tags\":" + tags + "}"
  if filelist.index(f) < (len(filelist) - 1):
    LIST += ","
  LIST += "\n"
LIST += "\t]\n}\n"
TAGS_TEMPLATE = TAGS_TEMPLATE.replace("[[DATA]]", LIST)
wfp = open("tags.html", 'w')
wfp.write(TAGS_TEMPLATE)
wfp.close()

# make about.html
rfp = open("template/post.template", 'r')
POST_TEMPLATE = rfp.read()
rfp.close()
POST_TEMPLATE = POST_TEMPLATE.replace("[[HEADER]]", HEADER)
POST_TEMPLATE = POST_TEMPLATE.replace("[[FOOTER]]", FOOTER)
POST_TEMPLATE = POST_TEMPLATE.replace("[[TITLE]]", TITLE)
rfp = open("posts/about.md", 'r')
POST = rfp.read()
rfp.close()
POST = POST_TEMPLATE.replace("[[DATA]]", POST)
wfp = open("posts/about.html", 'w')
wfp.write(POST)
wfp.close()
