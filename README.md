MP-IDS Honeypot
===============

This repository contains the generic **Connector** with configuration files in order to be used together with *Dionaea*.
Furthermore it contains configuration files for *Dionaea* to be used together with the generic *Connector* within the *Beemaster* project.

If you are interested in how the *Connector* and *Dionaea* work together with the other *Beemaster* components, have a look at the [integration test](https://git.informatik.uni-hamburg.de/iss/mp-ids/blob/master/Tests).


## Generic Connector

You find all information about using the generic *Connector* together with *Dionaea* in the [**connector**](connector) folder.
The following topics will be discussed:
* [Configuration of the *Connector*](connector//README.md#configuration)
* [Usage with and without Docker](connector//README.md#usage)
* [Setup development environment](connector//README.md#setup-development-environment)

## Dionaea Honeypot

You find all information about using *Dionaea* in a Docker environment and ready to use configurations in the [**dionaea**](dionaea) folder.

## Tip: Logging
* [Dionaea](dionaea/README.md#make-dionaea-stop-writing-files): Log a lot by default. It may be useful
* [Connector](connector/README.md#connection): Does not log by default. Depends on your start-script and settings. Seec