## Dionaea

This folder contains a working container setup for dionaea on alpine-linux basis.
You may want to read [milestone_durchstich](https://git.informatik.uni-hamburg.de/iss/mp-ids/blob/master/server/milestone-deployments/doku_milestone_durchstich.md) to see an example for dionaea sending incidents to a bro using broker.

### Build Dionaea Image

```docker build . -t dio-local```

Searches in the provided directory (here ```.```) for a ```Dockerfile```. Builds the image locally. The finished image is tagged (option ```-t```) with 'dio'. The tag can then be used for referencing the image.

### Run Docker Container

```docker run -p 21:21 80:80 -p 443:443 -p 445:445 -p 3306:3306 --name dio --rm dio-local```

Instanciate a container by reading the image called ```dio-local```. Flag ```-p``` maps container ports to ports on localhost. Flag ```--name dio``` is the container name (not image!). Container names are unique. ```--rm``` means, the container is thrown away on shutdown.

### Start Python Dummy Logger

So far, the you have to adjust the ihandler configuration to make dionaea send its logs via HTTP to "172.17.0.1:8080" to make them at the host machine available for the connector at "0.0.0.0:8080". The logging dummy offers a rest endpoint for that port and writes everything into a file.
The current setting is made to be working in a docker environment. See: [milestone_durchstich](https://git.informatik.uni-hamburg.de/iss/mp-ids/blob/master/server/milestone-deployments/doku_milestone_durchstich.md)

```python logging-dummy.py```
Use python3 here.

### Talk to Dionaea

Things are exposed to your local machine, so you can talk to your machine - which is then forwarded to the container.

```curl localhost```
Calls localhost on port 80.

```curl --insecure https://localhost```
Calls localhost on port 443, ssl.

```ftp localhost```
FTP to localhost.

```mysql --host=127.0.0.1```
mysql login to localhost. Always use 127.0.0.1, else mysql will use the `lo` interface and cannot connect.

Dionaea will pick this up, log a JSON string and send that to the dummy connector. The connector opens a file called ```log.txt``` and there you can find the dionaea output.

### Add Custom Service / Ihandler

Add whatever service or ihandler you want to ```services/``` or ```ihandlers/``` directory, respectively. Then you have to re-run ```docker build . -t dio-local```. (That step will not take as long as the first time). It will pick up the new files and copy them accordingly, to be used from within the container.


### Disable IHandlers:

So far, all default enabled IHandlers of dionaea are used. Those that are existing in our `services` and `ihandlers` folders only overwrite the defaults. If you want to explicitly disable a default, make a new ticket and lets discuss it there. **DO NOT `rm` something within our docker build, that is nonsense.**

### Make Dionaea stop (writing files)

##### Logging
**1.** Go to the `dionaea` folder and open the `dionaea.conf` file with an editor.

Change the logging levels to critical. As a result, there is almost nothing that
should be logged (except for critical errors like trying to write to `/dev/null`):
```
[logging]
default.levels=critical
errors.levels=critical
```

Alternatively, or if in doubt, you could change the logging file to `/dev/null`:

```
[logging]
default.levels=/dev/null
errors.levels=/dev/null
```

##### Downloading files
Go to the `dionaea` folder and open the `dionaea.conf` file with an editor.

Change the value of `download.dir` to `/dev/null`:

```
[dionaea]
download.dir=/dev/null
```

**Attention:** This results in critical errors of Dionaea. If you do not have
these in log files, you would need to write them to `/dev/null` too (see above).
