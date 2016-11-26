#!/usr/bin/env sh
# -*- coding: utf-8 -*-
#
# :: setup.sh
# Script to setup the necessary environment.
# This script does not setup any IDE-project.
# Use `./setup.sh -h` for more info.

_INSTALL=false
_VIRTUALENV=virtualenv
_ENVDIR=env
_REQUIREMENTS=requirements.txt
_ADDSOURCE=false
_SOURCENAME=pyenv

function error() { echo -e "\033[31;1m[ERR]\033[m$@" >&2; }
function error_exit() { error $@; exit 1; }

function usage() {
    echo -e "Usage: $0 [-h] [-i] [-r req] [-e env] [-a]

Options:
    -h          Print this help message and exit.
    -i          Install virtualenv, if not installed.
    -r req      Define the requirements.txt to use.
                (default: $_REQUIREMENTS)
    -e env      Define the environment directory.
                (default: $_ENVDIR)
    -a          Adds a symlink for easier environment sourcing.
                (use via '. $_SOURCENAME')"
    exit;
}

function parseargs() {
    while getopts ":hir:e:a" opt; do
        case $opt in
            h)
                usage ;;
            i)
                _INSTALL=true ;;
            r)
                _REQUIREMENTS=$OPTARG ;;
            e)
                _ENVDIR=$OPTARG ;;
            a)
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
    $_VIRTUALENV $_ENVDIR
    . $_ENVDIR/bin/activate
    pip install -r $_REQUIREMENTS
}

function addsource() {
    ln -sr $_ENVDIR/bin/activate $_SOURCENAME
    chmod +x $_SOURCENAME
}

parseargs $@

$_INSTALL && install
setup
$_ADDSOURCE && addsource
