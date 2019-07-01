# What is this?
This package contains library dockertarpusher that allows to push image packed as tar (usually from docker save command) to docker registry

Usage of library:

```
from dockertarpusher import Registry

reg = Registry("http://localhost:5000", "tests/busybox.tar", login = "admin", password = "admin123")
reg.processImage()

```

# Running
```
docker-tar-push {REGISTRYURL} {TARPATH} [login] [password] [--noSslVerify]
```


# Why?
Because sometimes you will need only to repush image to registry, without full access to docker socket, docker client, so why then volume the whole socket?


# License
Free to use (MIT)