#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'


docker run -d --name db arminc/clair-db:latest
docker run -p 6060:6060 --link db:postgres -d --name clair --restart on-failure arminc/clair-local-scan:v2.0.1
apk add -U wget ca-certificates
docker pull ${CI_APPLICATION_REPOSITORY}:${CI_APPLICATION_TAG}
wget https://github.com/arminc/clair-scanner/releases/download/v8/clair-scanner_linux_amd64
mv clair-scanner_linux_amd64 clair-scanner
chmod +x clair-scanner
touch clair-whitelist.yml
while( ! wget -q -O /dev/null http://docker:6060/v1/namespaces ) ; do sleep 1 ; done
retries=0
echo "Waiting for clair daemon to start"
while( ! wget -T 10 -q -O /dev/null http://docker:6060/v1/namespaces ) ; do sleep 1 ; echo -n "." ; if [ $retries -eq 10 ] ; then echo " Timeout, aborting." ; exit 1 ; fi ; retries=$(($retries+1)) ; done
./clair-scanner -c http://docker:6060 --ip $(hostname -i) -r gl-container-scanning-report.json -l clair.log -w clair-whitelist.yml ${CI_APPLICATION_REPOSITORY}:${CI_APPLICATION_TAG} || true
