import requests
import tarfile
import tempfile
import json
import os
from os import listdir
from os.path import isfile, join, isdir
import uuid
import hashlib
import json
import gzip
import shutil
from requests.auth import HTTPBasicAuth
from . import ManifestCreator

class Registry:
    def __init__(self, registryPath, imagePath, stream = False, login=None, password=None, sslVerify=True):
        self.registryPath = registryPath
        self.imagePath = imagePath
        self.login = login
        self.password = password
        self.auth = None
        self.stream = stream
        self.sslVerify = sslVerify
        if(self.login):
            self.auth = HTTPBasicAuth(self.login, self.password)
    
    def getManifest(self):
        return self.extractFromTarAndGetAsJson(self.imagePath, "manifest.json")

    def getConfig(self, name):
        return self.extractFromTarAndGetAsJson(self.imagePath, name)

    def extractFromTarAndGetFile(self, tarPath, fileToExtract):
        manifest = tarfile.open(tarPath)
        manifestStrFile = manifest.extractfile(fileToExtract)
        return manifestStrFile

    def readAndParseAsUtf8(self, toParse):
        manifestStr = (toParse.read()).decode("utf-8")
        toParse.close()
        return manifestStr

    def conditionalPrint(self, what, end=None):
        if(self.stream):
            if(end):
                print(what, end=end)
            else:
                print(what)

    def parseAsJson(self, toParse):
        return json.loads(toParse)

    def extractFromTarAndGetAsJson(self, tarPath, fileToParse):
        loaded = self.extractFromTarAndGetFile(tarPath, fileToParse)
        stringified = self.readAndParseAsUtf8(loaded)
        return self.parseAsJson(stringified)


    
    def extractTarFile(self, tmpdirname):
        tar = tarfile.open(self.imagePath)
        tar.extractall(tmpdirname)
        tar.close()
        return True


    def processImage(self):
        manifestFile = self.getManifest()[0]
        repoTags = manifestFile["RepoTags"]
        configLoc = manifestFile["Config"]
        configParsed = self.getConfig(configLoc)

        with tempfile.TemporaryDirectory() as tmpdirname:
            for repo in repoTags:
                image, tag = self.getImageTag(repo)
                self.conditionalPrint("[INFO] Extracting tar for " + image + " with tag: " + tag)
                self.extractTarFile(tmpdirname)
                layers = manifestFile["Layers"]
                for layer in layers:
                    self.conditionalPrint("[INFO] Starting pushing layer " + layer)
                    status, url = self.startPushing(image)
                    if(not status):
                        self.conditionalPrint("[ERROR] Something bad with starting upload")
                        return False
                    self.pushLayer(os.path.join(tmpdirname, layer), image, url)
                self.conditionalPrint("[INFO] Pushing config")
                status, url = self.startPushing(image)
                if(not status):
                    return False
                self.pushConfig(os.path.join(tmpdirname, configLoc), image, url)
                properlyFormattedLayers = []
                for layer in layers:
                    properlyFormattedLayers.append(os.path.join(tmpdirname, layer))
                creator = ManifestCreator(os.path.join(tmpdirname, configLoc), properlyFormattedLayers)
                registryManifest = creator.createJson()
                self.conditionalPrint("[INFO] Pushing manifest")
                self.pushManifest(registryManifest, image, tag)
                self.conditionalPrint("[INFO] Image pushed")
        return True
    
    def pushManifest(self, manifest, image, tag):
        headers = {"Content-Type": "application/vnd.docker.distribution.manifest.v2+json"}
        url = self.registryPath + "/v2/" + image + "/manifests/" + tag
        r = requests.put(url, headers=headers, data=manifest, auth = self.auth, verify = self.sslVerify)
        return r.status_code == 201


    def getImageTag(self, processing):
        splitted = processing.split(":")
        image = splitted[0]
        tag = splitted[1]
        return image, tag

    def startPushing(self, repository):
        self.conditionalPrint("[INFO] Upload started")
        r = requests.post(self.registryPath + "/v2/" + repository + "/blobs/uploads/", auth = self.auth, verify = self.sslVerify)
        uploadUrl = None
        if(r.headers.get("Location", None)):
            uploadUrl = r.headers.get("Location")
        return (r.status_code == 202), uploadUrl

    def pushLayer(self, layerPath, repository, uploadUrl):
        self.chunkedUpload(layerPath, uploadUrl)

    def pushConfig(self, layerPath, repository, uploadUrl):
        self.chunkedUpload(layerPath, uploadUrl)

    def getSha256OfFile(self, filepath):
        sha256hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            while True:
                data = f.read(2097152)
                sha256hash.update(data)
                if not data:
                    break
        return sha256hash.hexdigest()
        
    def read_in_chunks(self, file_object, hashed, chunk_size=2097152):
        while True:
            data = file_object.read(chunk_size)
            hashed.update(data)
            if not data:
                break
            yield data

    def setAuth(self, authObj):
        self.atuh = authObj

    def chunkedUpload(self, file, url):
        content_name = str(file)
        content_path = os.path.abspath(file)
        content_size = os.stat(content_path).st_size
        f = open(content_path, "rb")
        index = 0
        offset = 0
        headers = {}
        indexneu = 0 
        uploadUrl = url
        sha256hash = hashlib.sha256()
        
        for chunk in self.read_in_chunks(f, sha256hash):
            offset = index + len(chunk)
            headers['Content-Type'] = 'application/octet-stream'
            headers['Content-Length'] = str(len(chunk))
            headers['Content-Range'] = '%s-%s' % (index, offset)
            index = offset
            last = False
            if(offset == content_size):
                last = True
            try:
                self.conditionalPrint("Pushing... " + str(round((offset / content_size) * 100, 2)) + "%  ", end="\r" )
                if(last):
                    r = requests.put(uploadUrl + "&digest=sha256:" + str(sha256hash.hexdigest()), data=chunk, headers=headers, auth = self.auth, verify = self.sslVerify)
                else:
                    r = requests.patch(uploadUrl, data=chunk, headers=headers, auth = self.auth, verify = self.sslVerify)
                    if("Location" in r.headers):
                        uploadUrl = r.headers["Location"]

            except Exception as e:
                return False
        f.close()
        self.conditionalPrint("")

