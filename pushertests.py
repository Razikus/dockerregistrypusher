import unittest
import requests
import docker
from dockertarpusher import Registry

class TestPusher(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print("Setuping")
        print("Pulling registry...")
        client = docker.from_env()
        client.images.pull("registry:2.7.1")
    @classmethod
    def tearDownClass(self):
        print("Cleaning up")
        client = docker.from_env()
        try:
            client.containers.get("registrytest").remove(force=True)
        except:
            print("")
        try:
            client.volumes.get("registrytestvol").remove(force=True)
        except:
            print("")

    def startRegistry(self):
        client = docker.from_env()
        client.containers.run("registry:2.7.1", detach=True, ports={"5000/tcp": 5000}, name="registrytest", volumes={"registrytestvol": {"bind": "/var/lib/registry", "mode": "rw"}})

    def stopRegistry(self):
        client = docker.from_env()
        client.containers.get("registrytest").remove(force=True)
        client.volumes.get("registrytestvol").remove(force=True)

    def setUp(self):
        print("Starting clean registry")
        try:
            self.stopRegistry()
        except:
            print("Cannot stop registry, probably not exists")
        self.startRegistry()


    def testOneLayer(self):
        registryUrl = "http://localhost:5000"
        reg = Registry(registryUrl, "tests/busybox.tar")
        reg.processImage()
        r = requests.get(registryUrl + "/v2/_catalog")
        self.assertTrue("razikus/busybox" in r.json()["repositories"])
        r = requests.get(registryUrl + "/v2/razikus/busybox/tags/list")
        self.assertTrue("razikus/busybox" == r.json()["name"])
        self.assertTrue("1.31" in r.json()["tags"])

        
    def testOneLayerAndRun(self):
        registryUrl = "http://localhost:5000"
        reg = Registry(registryUrl, "tests/busybox.tar")
        reg.processImage()
        r = requests.get(registryUrl + "/v2/_catalog")
        self.assertTrue("razikus/busybox" in r.json()["repositories"])
        r = requests.get(registryUrl + "/v2/razikus/busybox/tags/list")
        self.assertTrue("razikus/busybox" == r.json()["name"])
        self.assertTrue("1.31" in r.json()["tags"])
        client = docker.from_env()
        client.images.pull("localhost:5000/razikus/busybox:1.31")
        client.containers.run("localhost:5000/razikus/busybox:1.31", remove=True)
        client.images.remove("localhost:5000/razikus/busybox:1.31")


    def testMultipleLayersWithDockerSave(self):
        client = docker.from_env()
        client.images.pull("razikus/whoami:slim80")
        image = client.images.get("razikus/whoami:slim80")
        f = open("tests/whoami.tar", "wb")
        for chunk in image.save(named = True):
            f.write(chunk)
        f.close()

        registryUrl = "http://localhost:5000"
        reg = Registry(registryUrl, "tests/whoami.tar")
        reg.processImage()
        r = requests.get(registryUrl + "/v2/_catalog")
        self.assertTrue("razikus/whoami" in r.json()["repositories"])
        r = requests.get(registryUrl + "/v2/razikus/whoami/tags/list")
        self.assertTrue("razikus/whoami" == r.json()["name"])
        self.assertTrue("slim80" in r.json()["tags"])


if __name__ == '__main__':
    unittest.main()

