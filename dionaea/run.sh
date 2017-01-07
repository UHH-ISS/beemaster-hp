#!/bin/sh

docker build . -t dio-local
docker run -p 21:21 -p 80:80 -p 443:443 -p 3306:3306 -p 445:445 --name dio --rm dio-local

# further smb port that could be exposed for testing purposes too
#-p 137:137 -p 138:138 -p 139:139 