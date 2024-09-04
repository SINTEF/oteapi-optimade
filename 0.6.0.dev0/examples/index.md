# Overview
<!-- markdownlint-disable MD046 -->

This section provides examples of how to use this OTEAPI plugin to perform OPTIMADE queries and handle the results.

In [_Use OTEAPI-OPTIMADE with OTElib_](otelib) you can find an example of how to use this plugin with the [OTElib](https://github.com/EMMC-ASBL/otelib) client.

It is worth noting that there are several different ways to use the strategies in this plugin.
For example, an OPTIMADE query can be provided using the `OPTIMADE` filter strategy, but it can also be provided directly in the URL value of the `OPTIMADE` data resource strategy's `accessUlr` parameter.
Further, it could be set through a `configuration` parameter entry to either of these strategies.

In the examples only one of these options are given, and this is the same for other aspects: What we believe is the most common and transparent use case is given.

Finally, it is important to note that using OTElib directly is not intended for end users.
Using OTElib should be done as a backend task in a web application, and the results should be presented to the end user in a more user friendly way.

## Setup for examples

### Prerequisites

To run the examples locally, you need to have the following tools available (in addition to a working Python 3.9+ installation):

- [Jupyter](https://jupyter.org/)
- [Docker](https://www.docker.com/) (or similar containerization tool)

#### Jupyter installation

To install Jupyter, please refer to the [Jupyter documentation](https://docs.jupyter.org/en/latest/install/notebook-classic.html).
If you want to use `pip` to install Jupyter, you can do so by installing the `examples` extra for this plugin package:

```bash
pip install oteapi-optimade[examples]
```

This will also install OTElib and any other Python packages you may need for the examples.

#### Docker installation

To install Docker, please refer to the [Docker documentation](https://docs.docker.com/get-docker/).

### Start a local OTEAPI server

When running a local OTEAPI server, you need to ensure the OTEAPI-OPTIMADE plugin is installed.
This can be done by using the `OTEAPI_PLUGIN_PACKAGES` environment variables as described in the [OTEAPI Services README](https://github.com/EMMC-ASBL/oteapi-services#oteapi-plugin-repositories).

There are two methods of starting the server:

1. [Using Docker](#using-docker)
1. [Using Docker Compose](#using-docker-compose)

No matter the method, the server will be available at `http://localhost:80/`.
To check it, go to the `/docs` endpoint: [localhost:80/docs](http://localhost:80/docs).

#### Using Docker

There are no extra files needed to start the server using Docker.
However, several commands need to be run to start the server, which is a collection of different microservices running in different containers on the same Docker network.

The general setup is outlined in the [OTEAPI Services README](https://github.com/EMMC-ASBL/oteapi-services#readme).

For convenience, the following commands can be used to start the services:

```bash
docker network create otenet
docker volume create redis-persist
docker run \
    --detach \
    --name redis \
    --volume redis-persist:/data \
    --network otenet \
    redis:latest
docker run \
    --rm \
    --network otenet \
    --detach \
    --publish 80:8080 \
    --env OTEAPI_REDIS_TYPE=redis \
    --env OTEAPI_REDIS_HOST=redis \
    --env OTEAPI_REDIS_PORT=6379 \
    --env OTEAPI_INCLUDE_REDISADMIN=False \
    --env OTEAPI_EXPOSE_SECRETS=True \
    --env OTEAPI_PLUGIN_PACKAGES=oteapi-optimade \
    ghcr.io/emmc-asbl/oteapi:1.20231108.329
```

!!! note
    To use the `/triples` endpoint, an AllegroGraph triplestore needs to be running.
    For more information see the [OTEAPI Services README](https://github.com/EMMC-ASBL/oteapi-services#run-a-triplestore-allegrograph) to see how to set this up and run it.

!!! important
    Pinning to version '1.20231108.329' of the OTEAPI image is important, as the latest version is currently not compatible with this plugin.
    To follow this issue, please see [GitHub issue #187](https://github.com/SINTEF/oteapi-optimade/issues/187) and [GitHub issue #163](https://github.com/SINTEF/oteapi-optimade/issues/163).

#### Using Docker Compose

Download the Docker Compose file from the [OTEAPI Services repository](https://github.com/EMMC-ASBL/oteapi-services/blob/master/docker-compose.yml):

```bash
curl -O https://raw.githubusercontent.com/EMMC-ASBL/oteapi-services/master/docker-compose.yml
```

And either update the `OTEAPI_PLUGIN_PACKAGES` environment variable in the file to include `oteapi-optimade`:

```yaml
# ...
      OTEAPI_PLUGIN_PACKAGES: oteapi-optimade
# ...
```

Or set the environment variable when starting the services by prefixing it to the Docker Compose command.

Then start the services:

```bash
docker compose pull
docker compose up --detach
```

!!! note
    When setting the environment variables as a prefix to the `docker compose` command, it is only needed for the command that runs the services:

    ```bash
    OTEAPI_PLUGIN_PACKAGES=oteapi-optimade docker compose up --detach
    ```
