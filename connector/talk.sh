#!/usr/bin/env sh

curl -XPOST -d '{"data": {"args": ["show databases"], "command": 3, "connection": {"id": 140273915464400, "local_ip": "172.17.0.2", "local_port": 3306, "protocol": "mysqld", "remote_hostname": "", "remote_ip": "172.17.0.1", "remote_port": 43682, "transport": "tcp"}}, "name": "dionaea", "origin": "dionaea.modules.python.mysql.command", "timestamp": "2016-12-20T18:23:27.488956"}' -H 'Content-type: application/json' localhost:8080/
