#!/bin/sh

/usr/bin/kill -9 `/usr/bin/ps ax|grep -v grep|grep connector|awk -F ' ' '{print $1}'`
