# FLOIP Results Ingestion with Nifi and Superset

A demo setup of [Apache NiFi](https://nifi.apache.org/) to ingest from a FLOIP Results endpoint, data storage in Postgres and visualization with [Apache Superset](https://superset.incubator.apache.org/) dashboards.

The demo sites can be accessed on https://nifi-floip-demo.onalabs.org/nifi/ for NiFi and https://floip-demo.onalabs.org for Superset with the same credentials as the local setup. See the [Pizza Survey dashboard](https://floip-demo.onalabs.org/superset/dashboard/1/) at https://floip-demo.onalabs.org/superset/dashboard/1/.


## Initialize the Setup

Bring up the setup with `docker-compose up`, it may take upto 3 minutes for all the services to be fully functional after docker image downloads.

    $ docker-compose up -d

> Ensure the avro directory has permissions to allow Apache NiFi to write to it.

    $ docker-compose exec -u root nifi chown -R nifi avro



## Dashboard

Access superset on your browser at http://localhost:8088, use the credentials:


    username: admin
    password: p@ssw0rd

> Set the auto-refresh interval time to 30 seconds on the dashboard by clicking on the arrow down icon `V` next to edit dashboard

There are 2 ways to update the [Pizza Survey dashboard](http://localhost:8088/superset/dashboard/1/):

1. Make submissions on the [Pizza Survey Form](https://enketo.ona.io/::YVTA) and wait for 3 minutes to see the changes reflected
2. Add new submissions locally by running the following curl command:

```
curl http://localhost:9090/floip -H "package_name: pizza_survey" -d '[["2019-07-09T13:47:05+00:00",1171290623824092,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","date","2019-07-04",null],["2019-07-09T13:47:05+00:00",1171290672224313,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","name","Pizzarea",null],["2019-07-09T13:47:05+00:00",1171290817424982,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","stars",4,null],["2019-07-09T13:47:05+00:00",1171291011025888,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","borough","Manhattan",null],["2019-07-09T13:47:05+00:00",1171291059426117,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","visited","yes",null],["2019-07-09T13:47:05+00:00",1171291156226578,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","location","-1.291449 36.787959 1 1",null]]'
```

> Note on new submissions:
> * The timestamp should be higher than that already on the dashboards to be considered an update. Edit all the timestamps in each row with the current timestamp.



## Nifi Flow Processor

Access the nifi processor at http://localhost:8080/nifi.

## AVRO Files

Avro formated flow results for Pizza Survey is stored in `pizza_survey.avro` file which can be accessed by getting into the avro volume via the nifi container.

    $ docker-compose exec nifi ls avro/
    $ docker-compose exec nifi ls avro/pizza_survey.avro
