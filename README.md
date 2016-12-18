MP-IDS Honeypot
===============

### Setup

> Linux install only. For development on Windows please setup manually.

```sh
./setup.sh -h
# Usage: ./setup.sh -h
#        ./setup.sh [-i|u] [-d] [-s]
#        ./setup.sh -c
#
# Options:
#     -h      Print this help message and exit.
#     -i      Install virtualenv, if not installed.
#     -u      Update environment(s) with new requirements.
#     -d      Setup development environment (for linting etc.)
#     -s      Adds symlinks for easier environment sourcing.
#     -c      Removes everything, created by this setup and exits.
```

#### Development

Execute `./setup.sh -d` to setup all required environments. `flake8` will be
accessible in the main directory so you do not necessarily need to source the
environment to use the linter (if sourced, `flake8` will be in your `PATH`).

#### Execution only

If you only need to run the code, use `./setup.sh` to install the minimal
environment.

Source the environment with `. env/bin/activate` (or use the symlink, provided
by `./setup.sh -s`). Be aware, that the activation only applies for the current
shell. Other shells/terminals/sessions need to source the environment again.

### Notes

> @1jost: Would [tox](https://tox.readthedocs.io/en/latest/) be overkill? It
> seems to be an awesome tool for environment and test management (primarily
> meant for CI).

### Code-Structure

Source directory: `connector`

As `python2` is used, code for `python3` compatibility.

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""<module-name>
<documentation>
"""

# :: Imports
<imports>

# :: Classes
<classes>

# :: Functions
<functions>

<if __name__ ... only if necessary>
```

- [STYLEGUIDE](https://git.informatik.uni-hamburg.de/iss/mp-ids/blob/master/STYLEGUIDE.md)
- https://google.github.io/styleguide/pyguide.html
