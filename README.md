# FLOIP Results Ingestion with Nifi and Superset

A demo setup of Apache NiFi and superset to ingest a FLOIP Results endpoint and visualization with Apache superset dashboards.


## Initialize the Setup

Bring up the setup with `docker-compose up`, it may take upto 3 minutes for all the services to be fully functional after docker image downloads.

    $ docker-compose up -d


## Dashboard

Access superset on your browser at http://localhost:8088, use the credentials:


    username: admin
    password: p@ssw0rd

There are 2 ways to update the Pizza Survey dashboard:

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
Avro formated flow results for Pizza Survey is stored in `pizza_survey.avro` file which can be accessed by getting into avro directory.

    $ cd nifi/avro
