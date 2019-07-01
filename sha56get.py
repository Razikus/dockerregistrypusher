import hashlib
import sys
import os



# print(sha256hash.hexdigest())
for subdir, dirs, files in os.walk(sys.argv[1]):
    for file in files:
        sha256hash = hashlib.sha256()
        with open(os.path.join(subdir, file), "rb") as f:
            sha256hash.update(f.read())
        print(os.path.join(subdir, file), sha256hash.hexdigest())
