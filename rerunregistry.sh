#!/bin/bash
docker rm -f registrytest
docker volume rm leo
docker run -e REGISTRY_AUTH="htpasswd" -e REGISTRY_AUTH_HTPASSWD_REALM='realm' -e REGISTRY_AUTH_HTPASSWD_PATH='/httpasswd_storage/htpasswd' -v /home/adam/htpasswd:/httpasswd_storage/htpasswd -p 5000:5000 -d -v leo:/var/lib/registry --name registrytest registry
