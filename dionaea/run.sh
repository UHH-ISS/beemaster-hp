#!/bin/sh

docker build . -t dio-local
docker run \
	-p 21:21 \
	-p 23:23 \
	-p 53:53 \
	-p 80:80 \
	-p 123:123 \
	-p 443:443 \
	-p 445:445 \
	-p 3306:3306 \
	--name dio --rm dio-local