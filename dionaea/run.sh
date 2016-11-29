#!/bin/sh

docker build . -t dio-local
docker run -p 21:21 -p 80:80 -p 443:443 -p 3306:3306 --name dio --rm dio-local