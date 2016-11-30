MP-IDS Honeypot
===============

### Setup

> Linux install only. For development on Windows please setup manually.

Execute `./setup.sh` to setup the virtual environment. Use `-h` for more
information. Source the environment with `. env/bin/activate` (or use the
symlink, provided by `./setupt.sh -s`). Be aware, that the activation only
applies for the current shell. Other shells/terminals/sessions need to source
the environment again.

### TODOs

- [x] add `requirements.txt`
    - [x] content
- [x] add `setup.sh`
    - [x] can setup `virtualenv`
    - [x] can add easier env-sourcing (VM provides `pyenv` command).
- [x] add `.gitignore`
- [x] set base structure
- [ ] set broker _(needs to be evaluated first)_

### Code-Structure

Source directory: `beemaster/connector`

If `python2` is used, code for `python3` compatibility.

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
