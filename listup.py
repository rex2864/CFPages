import os

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
  url = f.replace("%", "%25").replace("#", "%23").replace("$", "%24").replace("&", "%26").replace("+", "%2B").replace("-", "%2D").replace("?", "%3F").replace("@", "%40")
  date = fn[:4] + "-" + fn[4:6] + "-" + fn[6:8]
  title = fn[10:].replace("_", " ")
  tags = get_tags(f)
  fp.write("\t\t{\"url\":\"" + url + "\",\"date\":\"" + date + "\",\"title\":\"" + title + "\",\"tags\":" + tags + "}")
  if filelist.index(f) < (len(filelist) - 1):
    fp.write(",")
  fp.write("\n")
fp.write("\t]\n}\n")
fp.close()
