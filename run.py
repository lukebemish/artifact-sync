import os
import re
import requests
from requests.auth import HTTPBasicAuth

allowedVersion = os.environ['ALLOWED_VERSION']
allowedPaths = [re.compile("^"+i.replace('*','[^/]*')+"/") for i in os.environ['ALLOWED_PATHS'].split(',')]
mavenURL = os.environ['MAVEN_URL']
mavenUser = os.environ['MAVEN_USER']
mavenPass = os.environ['MAVEN_PASSWORD']

basic = HTTPBasicAuth(mavenUser, mavenPass)

root = os.path.join(os.getcwd(), "repo")

paths = set()

fullpaths = {}

metadatas = {}

for path, subdirs, files in os.walk(root):
    for name in files:
        outpath = os.path.relpath(os.path.join(path, name), root)
        for pattern in allowedPaths:
            if pattern.match(outpath):
                start = pattern.search(outpath).group(0)
                remaining = outpath[len(start):]
                if remaining.startswith(allowedVersion):
                    with open(os.path.join(path, name), 'rb') as f:
                        print(mavenURL + outpath)
                        headers = {
                            'User-agent': 'lukebemish/artifact-sync'
                        }
                        put = requests.put(mavenURL + outpath, auth=basic, data=f, headers=headers)
                        if put.status_code < 200 or put.status_code >= 300:
                            raise Exception("Failed to upload file: " + mavenURL + outpath + "; received status code " + str(put.status_code))

