# FLOIP Results Ingestion with Nifi and Superset

A demo setup of Apache NiFi and superset to ingest a FLOIP Results endpoint and visualization with Apache superset dashboards.


## Initialize the Setup

Bring up the setup with `docker-compose up`, it may take upto 3 minutes for all the services to be fully functional after docker image downloads.

    $ docker-compose up


## Dashboard

Access superset on your browser at http://localhost:8088, use the credentials:


    username: admin
    password: p@ssw0rd

For the Pizza Survey dashboard, you can add new submissions by running the following curl command: 

```
curl http://localhost:9090/floip -H "Content-Type: application/json" -H "package_name: pizza_survey" -d '[["2019-07-09T13:47:05+00:00",1171290623824092,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","date","2019-07-04",null],["2019-07-09T13:47:05+00:00",1171290672224313,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","name","Pizzarea",null],["2019-07-09T13:47:05+00:00",1171290817424982,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","stars",4,null],["2019-07-09T13:47:05+00:00",1171291011025888,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","borough","Manhattan",null],["2019-07-09T13:47:05+00:00",1171291059426117,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","visited","yes",null],["2019-07-09T13:47:05+00:00",1171291156226578,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","location","-1.291449 36.787959 1 1",null]]'
```

> Note on new submissions:
> The timestamp should be higher than that already on the dashboards to be considered an update. Edit all the timestamps in each row with the current timestamp.



## Nifi Flow Processor

Access the nifi processor at http://localhost:8080/nifi.
