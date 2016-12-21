#!/usr/bin/env sh

curl -XPOST -d '{"timestamp": "2016-11-26T22:18:56.281464", "data": {"connection": {"remote_ip": "127.0.0.1", "remote_hostname": "", "id": 3019197952, "protocol": "pcap", "local_port": 4101, "local_ip": "127.0.0.1", "remote_port": 35324, "transport": "tcp"}}, "name": "dionaea", "origin": "dionaea.connection.free"}' -H 'Content-type: application/json' localhost:8080/
