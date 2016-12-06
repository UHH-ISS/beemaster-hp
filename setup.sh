#!/usr/bin/env sh
# -*- coding: utf-8 -*-
#
# :: setup.sh
# Script to setup the necessary environment.
# This script does not setup any IDE-project.
# Use `./setup.sh -h` for more info.

function error() { echo -e "\033[31;1m[ERR]\033[m $@" >&2; }
function error_exit() { error $@; exit 1; }

_INSTALL=false
_UPDATE=false
_VIRTUALENV=virtualenv
_ENVDIR=env
_REQUIREMENTS=requirements.txt
_ADDSOURCE=false
_SOURCENAME=pyenv
_PYTHON2=$(which python2 2>/dev/null)
# TODO should -i try to install python2?
[ $? != 0 ] && error_exit "'python2' not found."
_BROKERLIBS=/usr/local/bro/lib/python/

function usage() {
    echo -e "Usage: $0 [-h] [-i|u] [-r req] [-e env] [-b path] [-s]

Options:
    -h          Print this help message and exit.
    -i          Install virtualenv, if not installed.
    -u          Update environment with new requirements.
    -r req      Define the requirements.txt to use.
                (default: $_REQUIREMENTS)
    -e env      Define the environment directory.
                (default: $_ENVDIR)
    -b path     Define the path to the broker python bindings.
                (default: $_BROKERLIBS)
    -s          Adds a symlink for easier environment sourcing.
                (use via '. $_SOURCENAME')"
    exit;
}

function parseargs() {
    while getopts ":hiur:e:b:s" opt; do
        case $opt in
            h)
                usage ;;
            i)
                _INSTALL=true ;;
            u)
                _UPDATE=true ;;
            r)
                _REQUIREMENTS=$OPTARG ;;
            e)
                _ENVDIR=$OPTARG ;;
            b)
                _BROKERLIBS=$OPTARG ;;
            s)
                _ADDSOURCE=true ;;
            \?|*)
                error_exit "Invalid argument -$OPTARG" ;;
        esac
    done
}

function install() {
    type virtualenv 2>/dev/null
    if [ $? != 0 ]; then
        type pacman 2>/dev/null
        if [ $? != 0 ]; then
            sudo pacman -S python-virtualenv
        else
            sudo python -m ensurepip
            sudo python -m pip install virtualenv
            _VIRTUALENV="python -m virtualenv"
        fi
    fi
}

function setup() {
    [ -d "$_BROKERLIBS" ] || error_exit "broker libraries not found."
    type virtualenv 2>/dev/null
    if [ $? != 0 ]; then
        python -m virtualenv 2>/dev/null
        [ $? != 0 ] && error_exit "'virtualenv' not found."
    fi
    # setting up the environment
    $_VIRTUALENV -p $_PYTHON2 $_ENVDIR
    . $_ENVDIR/bin/activate

    # installing requirements
    pip install -r $_REQUIREMENTS

    # adding broker bindings
    cd $_ENVDIR/lib/*/site-packages
    _so_path="$_BROKERLIBS/_pybroker.so"
    [ -e "$_so_path" ] || error_exit "'${_so_path##*/}' missing."
    ln -s "$_so_path" .
    _lib_path="$_BROKERLIBS/pybroker.py"
    _libc_path="${_lib_path}c"
    [ ! -e "$_lib_path" -a ! -e "$_libc_path" ] && error_exit "'$_lib_path' missing."
    [ -e "$_libc_path" ] && _lib_path="$_libc_path"
    ln -s "$_lib_path" .
}

function update() {
    [ -d "$_ENVDIR" ] || error_exit "environment '$_ENVDIR' not found."
    . $_ENVDIR/bin/activate
    pip install -r $_REQUIREMENTS
}

function addsource() {
    ln -sr $_ENVDIR/bin/activate $_SOURCENAME
    chmod +x $_SOURCENAME
}

parseargs $@

$_INSTALL && install
$_UPDATE && update || setup
$_ADDSOURCE && addsource
