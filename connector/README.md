# Connector

This connector accepts JSON-formatted input via HTTP, maps it to broker-compatible data types and sends a broker-message to a configurable endpoint.

# Configuration
## Connection
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
```

The positional argument accepts configuration files written in YAML with the following format:

```yaml
listen:
    address: 0.0.0.0            # Address to listen on.
    port: 8080                  # Port to listen on.
send:
    address: 127.0.0.1          # Address to send to.
    port: 5000                  # Port to send to.
mappings: mappings              # Directory to look for mappings.
broker:
    topic: honeypot/dionaea/    # Topic for sent messages.
    endpoint_prefix: beemaster-connector-             # Prefix name for the broker endpoint.
```
The values shown in the example above are the default that the connector falls back to, in case no arguments are passed to it.

## Mapping
The mappings used by the connector are configureable via YAML files. Below is an example of a mapping for a Dionaea connection event:

```yaml
# on file per connection type
#
# name: name of the event (for bro)
# mapping: the structure of the arriving json
#          to map to the desired broker-type
#          (implemented in mapper)
# message: the structure of the message, as it
#          will be put into the broker message
name: dionaea_connection
mapping:
    data:
        connection:
            id: string
            local_ip: address
            local_port: count
            remote_ip: address
            remote_port: count
            remote_hostname: string
            protocol: string
            transport: string
    timestamp: time_point
    origin: string
message:
    - timestamp
    - id
    - local_ip
    - local_port
    - remote_ip
    - remote_port
    - transport
```

Once you create a mapping, be sure to create the corresponding event handler on the other side of the connection.

# Usage
The Connector can be used as a Docker container, or locally for testing.

## With Docker

If you want to use the connector in conjunction with Dionaea and Bro containers, you can use the following Compose file (and make sure all directories are present, or change them accordingly).

By default (inside the container), the contents of the `conf` directory are copied into the `src` directory. Thus the `connector.py` can be started by passing the config file name directly (see the docker-compose file example below):

```yaml
version: '2'
services:
  connector:
    build: ./mp-ids-hp/connector
    command: ["config-docker.yaml"] 
  bro:
    build: ./mp-ids-bro
    volumes:
      - /var/beemaster/log/bro-master:/usr/local/bro/logs
  dionaea:
    build: ./mp-ids-hp/dionaea
```

Then run `docker-compose up --build`

Instead of passing `config-docker.yaml` as an argument (which is a config adjusted for this Compose file), you could also pass your own values, f.e.: 
```yaml
  connector:
    command: ["--sport","1337","--topic","leetevent/"]
```

You can also run the connector as a standalone container by appending the correct arguments to the `docker run` command:

```
docker build -t connector .
docker run connector --sport 1337 --topic leetevent/
```

## Without Docker

Start the connector via `python connector.py` and use the correct arguments for your environment. This repository holds a configuration file that can be used for local testing, which is identical to the default configuration, apart from sending to port 9999.

`python connector.py ../conf/config-local.yaml`

It will receive on port 8080 and dump a little text output to the console.
You can use the `talk.sh` script to send something to the connector.


