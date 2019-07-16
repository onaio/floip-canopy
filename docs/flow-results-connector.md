## FLOW RESULTS PACKAGE CONNECTOR

This connector is designed in Apache NiFi to automate the process of transferring flow-results packaged data to a table in a Postgres database or store AVRO formatted response results on disk. The connector ingests data in three different ways:

1. __Flow results API endpoint__
The schema for the table is derived from the descriptor of a package retrieved from `/flow-results/packages/[form_id]`. Once the schema for the table is generated, a table is created in the database. Data is then retrieved from the response endpoint: `/flow-results/packages/[form_id]/responses`. The connector requires a JSON configuration with the keys `form_id`, `base_url` and optionally, the `table_name` the user desires the data to be stored in. The JSON config can is formatted as below:

```
{
  "form_id": "[Data package id in UUID format]",
  "table_name": "[Preferred Postgres table name]",
  "base_url": "[Base URL to get data from]"	
}
```


> Note on API authentication
> For APIs that require authentication, edit processors that make GET requests to the API for survey and response named `GET flow results survey from API` and `GET flow results responses from API`. Enter the Basic Authentication Username and Basic Authentication Password or add a property for Authorization token by clicking `+` in properties.



2. __Survey and response JSON feed__
For JSON feed, under `Flow results JSON` processor, add the survey JSON to survey attribute and response JSON to the response attribute and custom text property.



3. __Published responses__
To push a FLOIP submission, a POST request is made to NiFi's URL port 9090 and `floip` endpoint. The package name or initially defined table name should be specified as part of the request headers which determines the Postgres table to be updated. Below is an example of a curl request:


```
curl http://localhost:9090/floip -H "package_name: pizza_survey" -d '[["2019-07-09T13:47:05+00:00",1171290623824092,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","date","2019-07-04",null],["2019-07-09T13:47:05+00:00",1171290672224313,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","name","Pizzarea",null],["2019-07-09T13:47:05+00:00",1171290817424982,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","stars",4,null],["2019-07-09T13:47:05+00:00",1171291011025888,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","borough","Manhattan",null],["2019-07-09T13:47:05+00:00",1171291059426117,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","visited","yes",null],["2019-07-09T13:47:05+00:00",1171291156226578,"john","cb398d5a-a039-4ee1-9ffb-16c6c68a8b4d","location","-1.291449 36.787959 1 1",null]]'
```



## Python Modules
The flow uses four scripts to flatten and transform flow results schema and responses:


1. __Create table statement parser__
This script takes in flow-results formatted survey together with table name if defined as parameters and returns a valid Postgres create table statement. The main function iterates through the `questions` object, getting column names from question key and column type from the type value. The column types are substituted from a dictionary containing a map of schema types to valid Postgres types. In the case of the table name not defined, the package attribute name is used. For this [pizza survey package descriptor](https://github.com/onaio/floip-canopy/blob/documentation/docs/fixtures/pizza_survey_package_descriptor.json) the following create table statement is returned:

```
CREATE TABLE pizza_survey(submission_uuid VARCHAR, date DATE, stars DOUBLE PRECISION, borough VARCHAR, name VARCHAR, visited VARCHAR, _location_latitude DOUBLE PRECISION, _location_longitude DOUBLE PRECISION, _location_altitude DOUBLE PRECISION, _location_accuracy DOUBLE PRECISION);
```
 

2. __Transform package responses__

A single flow-results response submission is transformed into a map between all questions to the corresponding value. The function creates a map between the question name(fifth element) and the response value (sixth element) then adds the session ID as the submission ID and returns the object created. For example the following submission is transformed as follows:
```
[
  [ "2017-05-23T13:35:37.356-04:00", 20394823948, 923842093, 10499221, "ae54d3", "female", {"option_order": ["male","female"]} ],
  [ "2017-05-23T13:35:47.012-04:00", 20394823950, 923842093, 10499221, "ae54d7", "chocolate", {} ]
]
```
Is transformed to:
```
{
    "submission_id": "10499221",
    "ae54d3": "female",
    "ae54d7": "chocolate"
}
```
 

3. __Flatten nested JSON__

The returned dictionary from the script above may have nested data. This is because some of the responses capture repeat group data in the context of ona forms. The flatten_json script flattens this data. This function returns a list of flattened dictionaries. For example:

```
{
    "submission_id": "10499221",
    "group1": [
        {
            "ae54d3": "female",
            "ae54d7": "chocolate"
        },
        {
            "ae54d3": "male",
            "ae54d7": "strawberry"
        }
    ] 
}
```

The above JSON is flattened to:
[
    {
        "submission_id": "10499221",
        "group1_ae54d3": "female",
        "group1_ae54d7": "chocolate"
    },
    {
        "submission_id": "10499221",
        "group1_ae54d3": "male",
        "group1_ae54d7": "strawberry"
    }
]


4. __Format geotypes__
 
This script receives an individual flattened dictionary. A geopoints object holds the latitude, longitude, altitude and accuracy details. These values are added as individual key-value pairs in the dictionary and returns a single flattened dictionary. For example:

```
{
    "location": "32.000 -1.000 10 1"
}
```

The above geopoint is transformed to:

```
{
    "_location_latitude": 32.000,
    "_location_longitude": -1.000,
    "_location_altitude": 10,
    "_location_precision": 1
}
```


## Flow results package flowchart

<img src="https://github.com/onaio/floip-canopy/blob/documentation/docs/images/floip_flowchart.png" alt="FLOIP flowchart" width="700" height="1500">