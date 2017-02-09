# Dionaea

We suggest using *Dionaea* in a dockerized environment. The following sections describe how to use *Dionaea* with the Docker files provided in this repository.

The following topics will be discussed:
* [Run Dionaea](#run-dionaea)
* [Test Dionaea](#rest-dionaea) - trigger incidents and check the output of iHandlers without using the *generic Connector*.
* [Configure Dionaea](#configure-dionaea) - configure *Dionaea* (adding services and enabling iHandlers to send incident to a *Connector*) and tips on [how to make *Dionaea* log less](#logging) (interesting for environments with little space like a *Raspberry Pi*).


## Run Dionaea
The following describes how to run *Dionaea* using Docker. Read the [official documentation](http://dionaea.readthedocs.io/en/latest/installation.html) if you are interested in running it locally

### Build Dionaea Docker Image
```docker build . -t dio-local```

Searches in the provided directory (here ```.```) for a ```Dockerfile```. Builds the image locally. The finished image is tagged (option ```-t```) with 'dio'. The tag can then be used for referencing the image.

### Run Docker Container

```docker run -p 21:21 -p 23:23 -p 53:53/udp -p 53:53 -p 80:80 -p 123:123/udp -p 443:443 -p 445:445 -p 3306:3306 --name dio --rm dio-local```

Instanciate a container by reading the image called ```dio-local```. Flag ```-p``` maps container ports to ports on localhost. Flag ```--name dio``` is the container name (not image!). Container names are unique. ```--rm``` means, the container is thrown away on shutdown.

You could also use a `docker-compose` file like [this](connector#with-docker) one.


## Test Dionaea

### Talk to Dionaea

Using the above `run` command, you can talk to your machine - which is then forwarded to the container.

```curl localhost```
Calls localhost on port 80.

```curl --insecure https://localhost```
Calls localhost on port 443 (SSL).

```ftp localhost```
FTP login to localhost.

```mysql --host=127.0.0.1```
MySQL login to localhost. Always use `127.0.0.1`. (Else MySQL will use the `lo` interface and cannot connect.)

*Dionaea* will pick this up, log a JSON string and send that to the address you entered in the iHandler configuration.

##### Try Exploits on Dionaea

You could try exploiting *Dionaea* using [Metasploit](/METASPLOIT.md).

### Log ihandler Output (Start Python Dummy Logger)
So far, the you have to adjust the ihandler configuration to make *Dionaea* send its logs via HTTP to `172.17.0.1:8080` to make them at the host machine available for the connector at `0.0.0.0:8080`. The logging dummy offers a rest endpoint for that port and writes everything into a file.
The current setting is made to be working in a docker environment.

```python logging-dummy.py```
Use python3 here.

You can find the *Dionaea* output in the `log.txt` file.


## Configure Dionaea
### Add Custom Service / iHandler

Add whatever service or iHandler you want to ```services/``` or ```ihandlers/``` directory, respectively. 
Then you have to re-run ```docker build . -t dio-local```. (That step will not take as long as the first time). 
It will pick up the new files and copy them accordingly, to be used from within the container.

### Disable iHandlers:
So far, only those iHandlers and Services existing in our `services` and `ihandlers` folders are used.
To enable an iHandler or Service, you have to put the right file in one of these folders and configure it properly.
For example, the sqlite logging is disabled by default. You may want to [enable it](http://dionaea.readthedocs.io/en/latest/ihandler/log_sqlite.html).

### Logging

**Hint:** If you use *Dionaea* in a Docker environment with our dockerfile,
dionaea gets started by the following command:
`dionaea -l all,-debug -L '*' -c /etc/dionaea/dionaea.conf`
The first two parameters are for logging (level, domain) to the terminal.
You could [save the output to a file on your host machine](https://git.informatik.uni-hamburg.de/iss/mp-ids/blob/master/server/milestone-deployments/dio-connector-bro-up.sh). 
As a result you do not need to enter the container to read the
`dionaea.log` end `dionaea-errors.log`. The order and formatting may differ, if
you use compose file to start up various Docker containers, as the terminal
output contains the output from all these containers.

Knowing this, you may decide to either remove `-l all,-debug -L '*'` from the 
command if you write the output to a logfile or disable file logging, for not
storing the same information twice.

##### Stop Logging to Files
If you want to prevent *Dionaea* from writing logs, 
open the `dionaea.conf` file and remove all the lines in the `[logging]` section.
Make sure though to leave the section header in place as Dionaea will crash otherwise.

If you still want *Dionaea* to log critical errors, you may change the settings accordingly:
Go to the `dionaea` folder and open the `dionaea.conf` file with an editor.

Change the logging levels to critical. As a result, there is almost nothing that
should be logged (except for critical errors like trying to write to `/dev/null`):
```
[logging]
default.levels=critical
errors.levels=critical
```

##### Stop Downloading files
In general, you should remove the `store.yaml` ihandler from the
`ihandlers-enabled` folder, if you do not wish files to be downloaded by
*Dionaea*. This ihandler is responsible for actually storing files.
Be aware that you will no longer receive `dionaea.download.complete`
incidents with hash values and information of the downloaded files.

###### FTP
The FTP service let everyone write to the set FTP root folder. The only way to
disable writing files, is to change the setting for the [FTP-service](dionaea/services/ftp.yaml)
and disable the service at all.

##### Persisting Downloaded Files 
Since we're using Docker, downloaded files (f.e. via FTP) will be lost when the container is stopped. 
If you wish to keep downloaded files, uncomment the two lines in the dionaea volumes section in 
docker-compose.yaml, so that it looks like this: 
```
...
  dionaea:
    build: ./dionaea
    volumes:
      - /var/beemaster/log/dionaea-logs:/var/dionaea/logs
      - /var/beemaster/dionaea/binaries:/var/dionaea/binaries/
      - /var/beemaster/dionaea/ftp:/var/dionaea/roots/ftp
...
```
Please be aware that this might pose a security risk, as you're enabling anyone to upload files
to your server, storing them persistently. Vulnerabilities in *Dionaea*, Docker or other software could
very well lead to a compromise of the host system.
