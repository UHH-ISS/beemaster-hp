## Dionaea

This folder contains a working container setup for dionaea on alpine-linux basis.
Maybe the dionaea image could be used as baseimage for the connector. If that does not work out, it may be necessary to use something like supervisor.d to run both - dio+connector - inside the same container. 

### build dionaea image

```docker build . -t dio-local```

Searches in the provided directory (here ```.```) for a ```Dockerfile```. Builds the image locally. The finished image is tagged (option ```-t```) with 'dio'. The tag can then be used for referencing the image.

### run docker container

```docker run -p 80:80 -p 443:443 --name dio --rm dio-local```

Instanciate a container by reading the image called ```dio-local```. Flag ```-p``` maps container ports to ports on localhost. Flag ```--name dio``` is the container name (not image!). Container names are unique. ```--rm``` means, the container is thrown away on shutdown. 

### start python dummy-logger

So far, the dionaea config inside this folder make dionaea send its logs via http to "localhost:5000". The logging dummy offers a rest endpoint for that port and writes everything into a file.

```python logging-dummy.py```
Use python3 here.

### Talk to Dionaea

Things are exposed to your local machine, so you can talk to your machine - which is then forwarded to the container.

```curl localhost:80```
Calls localhost on port 80.

Dionaea will pick this up, log a json string and send that to the dummy-connector. The connector opens a file called ```log.txt``` and there you can find the dionaea output.

### add custom service / ihandler

Add whatever service or ihandler you want to ```services/``` or ```ihandlers/``` directory, respectively. The you have to re-run ```docker build . -t dio-local```. (That step will not take as long as the first time). It will pick up the new files and copy them accordingly, to be used from within the container.
