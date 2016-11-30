#!/usr/bin/env sh

curl -XPOST -d '{"hi": "there"}' -H 'Content-type: application/json' localhost:8080/
