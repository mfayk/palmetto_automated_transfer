import os
from datetime import datetime
import hashlib

def filehash(filepath, blocksize=4096):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as fp:
        while 1:
            data = fp.read(blocksize)
            if data:
                sha.update(data)
            else:
                break
    return sha.hexdigest()




def compute_dir_index(path):
    files = []
    subdirs = []

    for root, dirs, filenames in os.walk(path):
        for subdir in dirs:
            subdirs.append(os.path.relpath(os.path.join(root, subdir), path))

        for f in filenames:
            files.append(os.path.relpath(os.path.join(root, f), path))
        
    index = {}
    for f in files:
        index[f] = os.path.getmtime(os.path.join(path, files[0]))

    return dict(files=files, subdirs=subdirs, index=index)

def compute_diff(dir_base, dir_cmp):
    data = {}
    data['deleted'] = list(set(dir_cmp['files']) - set(dir_base['files']))
    data['created'] = list(set(dir_base['files']) - set(dir_cmp['files']))
    data['updated'] = []
    data['deleted_dirs'] = list(set(dir_cmp['subdirs']) - set(dir_base['subdirs']))

    for f in set(dir_cmp['files']).intersection(set(dir_base['files'])):
        if dir_base['index'][f] != dir_cmp['index'][f]:
            data['updated'].append(f)

    return data



"""""
path = '/Users/max/Documents/biofilm'
files = []
subdirs = []

for root, dirs, filenames in os.walk(path):
    for subdir in dirs:
        subdirs.append(os.path.relpath(os.path.join(root, subdir), path))

    for f in filenames:
        files.append(os.path.relpath(os.path.join(root, f), path))

#print(files)
#print(subdirs)


file_mtime = os.path.getmtime(os.path.join(path, files[0]))

file_mtime, datetime.fromtimestamp(file_mtime)

file_hash = filehash(os.path.join(path, files[0]))


print(file_hash)

index = {}
for f in files:
    index[f] = os.path.getmtime(os.path.join(path, files[0]))

diff = compute_dir_index(path)



while(1):
    diff2 = compute_dir_index(path)
    data = compute_diff(diff2, diff)
    print(data)

    if(bool(data.get('deleted')) == True or bool(data.get('created')) == True or bool(data.get('updated')) == True or bool(data.get('deleted_dirs')) == True):
        print("change found")
        print(data)
        diff = diff2





"""


