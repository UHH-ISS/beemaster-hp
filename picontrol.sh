#!/usr/bin/env sh
#
# ./picontrol.sh conn|dio start|stop

module="$1"
action="$2"

function error() { echo -e "\033[31mERROR\033[m $@"; }
function invarg() { error "Invalid argument. First argument has to be either '$1' or '$2'."; exit 1; }
function info() { echo -e "\033[33mINFO\033[m $@"; }

export PATH="${PATH}:/usr/bin"
conndir="/home/beemaster/mp-ids/mp-ids-hp/connector"

if [ "$1" == "conn" ]; then
    if [ "$2" == "start" ]; then
        info "Starting connector"
        python2 $conndir/src/connector.py $conndir/conf/config-rpi.yaml
    elif [ "$2" == "stop" ]; then
        info "Stopping connector"
        kill -9 $(/usr/bin/ps ax | grep -v grep | grep connector | awk -F' ' '{print $1}')
    else
        invarg start stop
    fi
elif [ "$1" == "dio" ]; then
    if [ "$2" == "start" ]; then
        info "Starting dionaea"
        docker build -f=dionaea/Dockerfile_Pi -t dio-local dionaea/
        docker run -p 21:21 -p 80:80 -p 443:443 -p 3306:3306 -p 445:445 --name dio --rm dio-local
    elif [ "$2" == "stop" ]; then
        info "Stopping dionaea"
        docker kill dio
        docker rm dio
    else
        invarg start stop
    fi
else
    invarg conn dio
fi
