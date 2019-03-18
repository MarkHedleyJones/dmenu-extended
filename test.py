import os
import subprocess
import time
import sys

watchdir = os.path.expanduser('~')

prefs = {}

prefs['include_hidden_files'] = False
prefs['include_hidden_folders'] = False
follow_symlinks = False
ignore_folders = []
prefs['scan_hidden_folders'] = False
valid_extensions = []

files_a = []
files_b = []

time_a_start = time.time()
files_a = subprocess.check_output(['find', watchdir]).split('\n')
if prefs['include_hidden_files'] == False:
  files_a = filter(lambda x: x.find("/.") == -1, files_a)



time_a_end = time.time()

# sys.exit()
# print(files_a)
print("a = {time} sec".format(time=round(time_a_end - time_a_start,2)))

time_b_start = time.time()
for root, dirs , files in os.walk(watchdir, followlinks=follow_symlinks):
    dirs[:] = [d for d in dirs if os.path.join(root,d) not in ignore_folders]
    if prefs['scan_hidden_folders'] or root.find('/.')  == -1:
        for name in files:
            if prefs['include_hidden_files'] or name.startswith('.') == False:
                # if valid_extensions == True or os.path.splitext(name)[1].lower() in valid_extensions:
                files_b.append(os.path.join(root,name))
        for name in dirs:
            if prefs['include_hidden_folders'] or name.startswith('.') == False:
                files_b.append(os.path.join(root,name) + '/')
time_b_end = time.time()

print("b = {time} sec".format(time=round(time_b_end - time_b_start,2)))

for f in files_a:
  if f not in files_b:
    print(f, ' in a but not in b')



