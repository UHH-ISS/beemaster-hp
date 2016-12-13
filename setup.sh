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
# TODO should DEVSETUP be true per default?
_DEVSETUP=false
_ADDSOURCE=false

_ENVDIR=env
_REQUIREMENTS=requirements.txt
_DEV_REQUIREMENTS=dev-requirements.txt
_SOURCENAME=pyenv

_VIRTUALENV=virtualenv
_PYTHON2=$(which python2 2>/dev/null)
# TODO should -i try to install python2?
[ $? != 0 ] && error_exit "'python2' not found."
_BROKERLIBS=/usr/local/bro/lib/python/


function usage() {
    echo -e "Usage: $0 -h
       $0 [-i|u] [-d] [-s]
       $0 -c

Options:
    -h      Print this help message and exit.
    -i      Install virtualenv, if not installed.
    -u      Update environment(s) with new requirements.
    -d      Setup development environment (for linting etc.)
    -s      Adds symlinks for easier environment sourcing.
    -c      Removes everything, created by this setup and exits.

Default variables:
    INSTALL             = $_INSTALL
    UPDATE              = $_UPDATE
    DEVSETUP            = $_DEVSETUP
    ADDSOURCE           = $_ADDSOURCE

    ENVDIR              = $_ENVDIR
    REQUIREMENTS        = $_REQUIREMENTS
    DEV_REQUIREMENTS    = $_DEV_REQUIREMENTS
    SOURCENAME          = $_SOURCENAME

    VIRTUALENV          = $_VIRTUALENV  ('python2 -m virtualenv' might be used)
    PYTHON2             = $_PYTHON2
    BROKERLIBS          = $_BROKERLIBS"
    exit
}

function parseargs() {
    while getopts ":hiudsc" opt; do
        case $opt in
            h)
                usage ;;
            i)
                _INSTALL=true ;;
            u)
                _UPDATE=true ;;
            d)
                _DEVSETUP=true ;;
            s)
                _ADDSOURCE=true ;;
            c)
                clean
                exit ;;
            \?|*)
                error_exit "Invalid argument -$OPTARG" ;;
        esac
    done
}

function clean() {
    rm -rf $_ENVDIR $_SOURCENAME flake8 .git/hooks/pre-commit
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

    current_dir="$(pwd)"

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
    cd "$current_dir"

    if $_DEVSETUP; then
        . $_ENVDIR/bin/activate
        pip install -r $_DEV_REQUIREMENTS
        git config --bool flake8.strict true
        git config --bool flake8.lazy true
        deactivate 2>/dev/null
        ln -sr $_ENVDIR/bin/flake8 .
        ln -sr pre-commit .git/hooks/
    fi
    deactivate 2>/dev/null
}

function update() {
    [ -d "$_ENVDIR" ] || error_exit "environment '$_ENVDIR' not found."
    . $_ENVDIR/bin/activate
    pip install -r $_REQUIREMENTS
    if $_DEVSETUP; then
        . $_ENVDIR/bin/activate
        pip install -r $_DEV_REQUIREMENTS
    fi
    deactivate 2>/dev/null
}

function addsource() {
    ln -sr $_ENVDIR/bin/activate $_SOURCENAME
    chmod +x $_SOURCENAME
}

parseargs $@

$_INSTALL && install
$_UPDATE && update || setup
$_ADDSOURCE && addsource
