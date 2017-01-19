#!/bin/sh

/usr/bin/docker build -f /home/beemaster/mp-ids/mp-ids-hp/dionaea/Dockerfile_Pi -t dio-local
/usr/bin/docker run -p 21:21 -p 80:80 -p 443:443 -p 3306:3306 -p 445:445 --name dio --rm dio-local
