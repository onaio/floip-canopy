# FLOIP Results Ingestion with Nifi and Superset

A demo setup of Apache NiFi and superset to ingest a FLOIP Results endpoint and visualization with Apache superset dashboards.


## Initialize the Setup

Bring up the setup with `docker-compose up`, it may take upto 3 minutes for all the services to be fully functional after docker image downloads.

    $ docker-compose up


## Dashboard

Access superset on your browser at http://localhost:8088, use the credentials:


    username: admin
    password: p@ssw0rd

For the Pizza Survey dashboard, you can make submissions on the [Pizza Survey Form](https://enketo.ona.io/::YVTA) to see the changes reflected.


## Nifi Flow Processor

Access the nifi processor at http://localhost:8080/nifi.
