import os
import hashlib
import json

class ManifestCreator():
    def __init__(self, configPath, layersPaths):
        self.configPath = configPath
        self.layersPaths = layersPaths
    
    def createJson(self):
        resultDict = dict()
        resultDict["schemaVersion"] = 2
        resultDict["mediaType"] = "application/vnd.docker.distribution.manifest.v2+json"
        resultDict["config"] = dict()
        resultDict["config"]["mediaType"] = "application/vnd.docker.container.image.v1+json"

        resultDict["config"]["size"] = self.getSizeOf(self.configPath)
        resultDict["config"]["digest"] = self.getSha256ProperlyFormatted(self.configPath)

        resultDict["layers"] = []
        for layer in self.layersPaths:
            layerDict = dict()
            layerDict["mediaType"] = "application/vnd.docker.image.rootfs.diff.tar"
            layerDict["size"] = self.getSizeOf(layer)
            layerDict["digest"] = self.getSha256ProperlyFormatted(layer)
            resultDict["layers"].append(layerDict)


        return json.dumps(resultDict)

    def getSizeOf(self, path):
        return os.path.getsize(path)
    def getSha256OfFile(self, filepath):
        sha256hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            while True:
                data = f.read(65536)
                sha256hash.update(data)
                if not data:
                    break
        return sha256hash.hexdigest()
        
    def getSha256ProperlyFormatted(self, filepath):
        return "sha256:" + self.getSha256OfFile(filepath)