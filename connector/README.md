Connector
=========

This connector accepts JSON-formatted input via HTTP, maps it to broker-compatible data types and sends a broker-message to a configurable endpoint.

## Configuration
### Connection
Connection-related settings of the connector can be configured via passing arguments at start or specifying a config file. The following arguments are supported:

```
positional arguments:
  file                  Configuration-file to use.

optional arguments:
  -h, --help            show this help message and exit
  --laddr address       Address to listen on.
  --lport port          Port to listen on.
  --saddr address       Address to send to.
  --sport port          Port to send to.
  --mappings directory  Directory to look for mappings.
  --topic topic         Topic for sent messages.
  --endpoint_prefix name       Prefix name for the broker endpoint.
  --id connector_id            This connector's unique id.
  --log-file file       The file to log to. 'stderr' and 'stdout' work as special names for standard-error and -out respectively.
  --log-level level     Set the log-level. {'INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL'}
  --log-datefmt format  Set the date/time format to use for logging ('asctime' placeholder in log-format). Python's strftime format is used.
  --log-format format   Set the logging format. Use the 'asctime' placeholder to include the date. See the python docs for more information on this.
```

The positional argument accepts configuration files written in YAML with the following format:

```yaml
listen:
    address: 0.0.0.0                        # Address to listen on.
    port: 8080                              # Port to listen on.
send:
    address: 127.0.0.1                      # Address to send to.
    port: 5000                              # Port to send to.
mappings: mappings                          # Directory to look for mappings.
broker:
    topic: honeypot/dionaea/                # Topic for sent messages.
    endpoint_prefix: beemaster-connector-   # Prefix name for the broker endpoint.
```
The values shown in the example above are the default that the connector falls back to, in case no arguments are passed to it.

By default, the connector uses the hostname to identify itself. You can change it to whatever name you like, but it should be a unique name in your network:
```yaml
connector_id: my_unique_connector_name       # Remove this to use the hostname by default
```

Furthermore, the connector is able to write logs. Just let him know in what information you are interested in:
```yaml
logging:
    file: stderr
    level: ERROR
    datefmt: None
    format: "[ %(asctime)s | %(name)10s | %(levelname)8s ] %(message)s"
```
Tip: Writing the `INFO` level to `stdout` or a file, mounted by the host to the docker container, makes it easier to
  see the traffic throughput of the connector.

### Mapping
The mappings used by the connector are configurable via YAML files. Below is an example of a mapping for a Dionaea access event:

```yaml
# one file per access type
#
# name: name of the event (for bro)
# mapping: the structure of the arriving json
#          to map to the desired broker-type
#          (implemented in mapper)
# message: the structure of the message, as it
#          will be put into the broker message
name: dionaea_access
mapping:
    timestamp: time_point
    src_hostname: string
    src_ip: address
    src_port: port_count
    dst_ip: address
    dst_port: port_count
    connection:
        type: string
        protocol: string
        transport: string
message:
    - timestamp
    - dst_ip
    - dst_port
    - src_hostname
    - src_ip
    - src_port
    - transport
    - protocol
```

Once you create a mapping, be sure to create the corresponding event handler on the other side of the connection.

## Usage
The Connector can be used as a Docker container, or locally for testing.
We advise you to run the Connector always on the same host as the Dionaea honeypot.

### With Docker

If you want to use the Connector in conjunction with Dionaea, you can use the following Compose file (and make sure all directories are present, or change them accordingly).

By default (inside the container), the contents of the `conf` directory are copied into the `src` directory. Thus the `connector.py` can be started by passing the config file name directly (see the docker-compose file example below):

```yaml
version: '2'
services:
  connector:
    build: ./mp-ids-hp/connector
    command: ["config-docker.yaml"]
  dionaea:
    build: ./mp-ids-hp/dionaea
    ports:
      - "21:21"
      - "80:80"
      - "443:443"
      - "445:445"
      - "3306:3306"
```

Then run `docker-compose up --build`

Be sure to expose only the ports of Dionaea you want to be accessable to attackers.

Instead of passing `config-docker.yaml` as an argument (which is a config adjusted for this Compose file), you could also pass your own values, e.g.: 
```yaml
  connector:
    command: ["--sport","1337","--topic","leetevent/"]
```

You can also run the connector as a standalone container by appending the correct arguments to the `docker run` command:

```
docker build -t connector .
docker run connector --sport 1337 --topic leetevent/
```

**For testing purposes** you might want to run Dionaea and the Connector 
together with Bro. To do so, use [this compose file](https://git.informatik.uni-hamburg.de/iss/mp-ids-bro/blob/master/docker-compose.yml).

### Without Docker

Start the connector via `python connector.py` and use the correct arguments for your environment. This repository holds a configuration file that can be used for local testing, which is identical to the default configuration, apart from sending to port 9999. Don't forget to ensure that you still sourced your environment as described [here](https://git.informatik.uni-hamburg.de/iss/mp-ids-hp/blob/master/README.md) because the connector still needs to run on python 2 and requires modules which aren't located in the `src` folder but included in the environment.

`python connector.py ../conf/config-local.yaml`

It will receive on port 8080 and dump a little text output to the console.
See [Dionaea Readme](dionaea/README.md#talk-to-dionaea) for information about how to communicate with it.

