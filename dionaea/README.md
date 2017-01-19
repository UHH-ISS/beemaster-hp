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

Using the above `run` command, you can talk to your machine - which is then forwarded to the container.

```curl localhost```
Calls localhost on port 80.

```curl --insecure https://localhost```
Calls localhost on port 443, ssl.

```ftp localhost```
FTP to localhost.

```mysql --host=127.0.0.1```
mysql login to localhost. Always use 127.0.0.1, else mysql will use the `lo` interface and cannot connect.

Dionaea will pick this up, log a JSON string and send that to the address you entered in the iHandler configuration.
In case of the [dummy logger](#start-python-dummy-logger), the you can find the Dionaea output in the  ```log.txt``` file.

##### Try exploits on Dionaea

You could try exploiting Dionaea using [Metasploit](/METASPLOIT.md)

### Add Custom Service / iHandler

Add whatever service or ihandler you want to ```services/``` or ```ihandlers/``` directory, respectively. 
Then you have to re-run ```docker build . -t dio-local```. (That step will not take as long as the first time). 
It will pick up the new files and copy them accordingly, to be used from within the container.


### Disable iHandlers:

So far, only those iHandlers and Services existing in our `services` and `ihandlers` folders are used.
To enable an iHandler or Service, you have to put the right file in one of these folders and configure it properly.
For example, the sqlite logging is disabled by default. You may want to [enable it](http://dionaea.readthedocs.io/en/latest/ihandler/log_sqlite.html).

### Make Dionaea stop (writing files)

##### Logging
If you want to prevent Dionaea from writing logs, simply open the `dionaea.conf`
file and remove all the lines in the `[logging]` section. Make sure though to
leave the section header in place as Dionaea will crash otherwise.


If you want Dionaea still log critical errors, you may change the settings accordingly:
**1.** Go to the `dionaea` folder and open the `dionaea.conf` file with an editor.

Change the logging levels to critical. As a result, there is almost nothing that
should be logged (except for critical errors like trying to write to `/dev/null`):
```
[logging]
default.levels=critical
errors.levels=critical
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
