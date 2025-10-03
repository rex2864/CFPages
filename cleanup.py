import os

if os.path.exists("index.html"):
  os.remove("index.html")
if os.path.exists("archive.html"):
  os.remove("archive.html")
if os.path.exists("tags.html"):
  os.remove("tags.html")
if os.path.exists("posts/about.html"):
  os.remove("posts/about.html")

filelist = []
for path, subdirs, files in os.walk("posts/"):
  for name in files:
    if name[-5:] == ".html":
      f = os.path.join(path, name)
      if os.path.exists(f):
        os.remove(f)
