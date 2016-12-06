MP-IDS Honeypot
===============

### Setup

> Linux install only. For development on Windows please setup manually.

Execute `./setup.sh` to setup the virtual environment. Use `-h` for more
information. Source the environment with `. env/bin/activate` (or use the
symlink, provided by `./setup.sh -s`). Be aware, that the activation only
applies for the current shell. Other shells/terminals/sessions need to source
the environment again.

### Notes

> @1jost: Would [tox](https://tox.readthedocs.io/en/latest/) be overkill? It
> seems to be an awesome tool for environment and test management (primarily
> meant for CI).

### Code-Structure

Source directory: `beemaster/connector`

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

https://google.github.io/styleguide/pyguide.html
