#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""tests

Run all tests.
"""
from os.path import dirname, abspath
from os import getcwd, chdir
import unittest


class Cwd(object):
    """Context manager for current working directory"""

    def __init__(self, cwd):
        """Init Cwd with the directory to switch to"""
        self.cwd = cwd

    def __enter__(self):
        """Enter context"""
        self.old_cwd = getcwd()
        chdir(self.cwd)

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit context"""
        chdir(self.old_cwd)


if __name__ == '__main__':
    with Cwd(dirname(abspath(__file__))):
        # INFO As we do not use unittest.main(), there is no argument-handling.
        #      As a result, verbosity is set hard to 2 (equals -v flag).
        suite = unittest.defaultTestLoader.discover('.')
        unittest.TextTestRunner(verbosity=2).run(suite)
