"""
Generates a postgres table schema from flow results
"""

import json
import uuid
import re

JYTHON_AVAILABLE = True

try:
    # This is used in the NiFi ExecuteScript context
    import java.io  # pylint: disable=unused-import
    from org.apache.commons.io import IOUtils
    from java.nio.charset import StandardCharsets
    from org.apache.nifi.processor.io import StreamCallback
except ImportError:
    JYTHON_AVAILABLE = False
    print "Skipping Jython imports"


# Maximum identifier length supported in postgres
POSTGRES_MAX_IDENTIFIER_LENGTH = 63

# Geotypes appended words are '_altitude' and '_accuracy' of length 9
GEOTYPES_APPEND_WORD_LENGTH = 9

# Using a seed will allow UUID to be reproducible even in fail cases
FAIL_CASE_SEED = "i0em6a4qn"

# Accommodates the random string (_XXXX_) to be added to field_name
RANDOM_STRING_LENGTH = 6

# Mapping between FLOIP schema datatypes to corresponding sql datatypes
DATATYPE_MAPPING = {
    "date": "DATE",
    "time": "TIME",
    "datetime": "TIMESTAMP",
    "decimal": "DOUBLE PRECISION",
    "integer": "INTEGER",
    "select_one": "VARCHAR",
    "select_many": "VARCHAR",
    "open": "VARCHAR",
    "numeric": "DOUBLE PRECISION",
    "text": "VARCHAR",
    "calculate": "VARCHAR"
}


def remove_special_characters(name):
    """
    Function replaces special characters with an underscore.
    """

    name = re.sub(r"[-\\\(\),\.:;'\[\]\?\/\|{}\?><!@#\$%\^&\*\+ ]", '_', name)
    return name


def random_string_generator(field_name, retry_counter):
    """
    Function returns a random string with field_name as the seed.
    Incase the random string generated isn't unique, the seed used is a 
    predefined string called FAIL_CASE_SEED. This string is concatenated 
    to itself based on the number of retries. It is important to use a seed,
    so that the same random string can be reproduced.
    """

    if retry_counter == 0:
        random_string = str(uuid.uuid5(uuid.NAMESPACE_DNS,
                                       field_name.encode('utf-8')))
    else:
        new_fail_case_seed = FAIL_CASE_SEED * retry_counter
        random_string = str(uuid.uuid5(uuid.NAMESPACE_DNS,
                                       new_fail_case_seed.encode('utf-8')))
    return random_string[0:4]


def check_long_name(field_name, long_to_truncated_name_map,
                    appended_word_length=0):
    """Function shortens field_names longer than 63 characters"""
    retry_counter = 0
    find_shortened_field_name = True
    field_name_length = len(field_name)
    if (field_name_length + appended_word_length) <= \
        POSTGRES_MAX_IDENTIFIER_LENGTH:
        return field_name, long_to_truncated_name_map
    else:
        truncation_length = field_name_length + appended_word_length \
                            + RANDOM_STRING_LENGTH\
                            - POSTGRES_MAX_IDENTIFIER_LENGTH
        random_string = random_string_generator(field_name, retry_counter)
        half_field_name_length = field_name_length // 2
        half_truncation_length = (truncation_length + 1) // 2

        while find_shortened_field_name:
            random_string = random_string_generator(field_name, retry_counter)
            shortened_field_name = "{a}_{b}_{c}".format(
                a = field_name[0:(half_field_name_length
                                  - half_truncation_length)],
                b = random_string,
                c = field_name[(half_field_name_length
                                + half_truncation_length):])
            if shortened_field_name not in long_to_truncated_name_map.values():
                find_shortened_field_name = False
            else:
                retry_counter += 1

        long_to_truncated_name_map[field_name] = shortened_field_name
    return shortened_field_name, long_to_truncated_name_map

def geopoint_field_to_type_string(field_name, long_to_truncated_name_map):
    """
    A geopoint has latitude, longitude, altitude and accuracy values.
    The column_name_type_string generated has a column_name and column_type
    for each of these.
    """

    processed_name, truncated_name_map = check_long_name(
        field_name, long_to_truncated_name_map, GEOTYPES_APPEND_WORD_LENGTH)
    column_name_type_string = \
    "_{a}{b} {c},_{a}{d} {c},_{a}{e} {c},_{a}{f} {c}".format(
        a = processed_name, 
        b = "_latitude",
        c = "DOUBLE PRECISION",
        d = "_longitude",
        e = "_altitude",
        f = "_accuracy")
    return column_name_type_string, truncated_name_map


def create_table_statement_parser(flow_results_package,
                                                    table_name):
    """
    Parses floip schema to identify column names and types and generate
    create table statement
    """

    questions = flow_results_package["data"]["attributes"]["resources"]\
        [0]["schema"]["questions"]

    # Table name can be user defined or in the absence of this, gotten from
    # the title atribute in the FLOIP schema
    table_name = table_name or remove_special_characters(
        flow_results_package["data"]["attributes"]["title"])
    table_columns = ["submission_uuid VARCHAR"]
    long_to_truncated_names_map = {}
    geopoints = []

    for key, value in questions.iteritems():
        column_name = remove_special_characters(key)
        if value.get("type") == "geo_point":
            column_name_type_string, truncated_name_map \
                = geopoint_field_to_type_string(column_name,
                long_to_truncated_names_map)
            geopoints.append(
                long_to_truncated_names_map.get(column_name) or column_name)
            table_columns.append(column_name_type_string)
        else:
            processed_name, truncated_name_map = check_long_name(
                column_name, long_to_truncated_names_map)
            table_columns.append("{} {}".format(
                processed_name, 
                DATATYPE_MAPPING[value.get("type")] or "VARCHAR"))

        long_to_truncated_names_map.update(truncated_name_map)

    table_statement = "CREATE TABLE {}({});".format(table_name,
                                                    ",".join(table_columns))
    return table_statement, long_to_truncated_names_map, geopoints

if JYTHON_AVAILABLE:
    # pylint:disable=too-few-public-methods,invalid-name,undefined-variable
    class PyStreamCallback(StreamCallback):
        """
        Class to handle flowFile stream maninpulation.
        """

        def __init__(self):
            self.long_field_names_map = {}
            self.table_statement = ""
            self.geopoints = []

        def process(self, inputStream, outputStream):
            """
            Takes a flowfile as an input and outputs the transformed flowfile
            """
            self.table_statement, self.long_field_names_map, self.geopoints = \
                create_table_statement_parser(survey_json, table_name)

            outputStream.write(bytearray(
                json.dumps(self.table_statement, indent=4).encode('utf-8')))

    # session is provided by the NiFi ExecuteScript context
    flowFile = session.get()  # noqa
    if flowFile is not None:
        table_name = flowFile.getAttribute('table_name')
        survey_json = json.loads(flowFile.getAttribute('survey'))
        PROCESSED_DATA = PyStreamCallback()
        session.write(flowFile, PROCESSED_DATA)  # noqa
        ATTRMAP = {
            'table_statement': PROCESSED_DATA.table_statement,
            'geopoints': json.dumps(PROCESSED_DATA.geopoints),
            'long_field_names_map': json.dumps(
                PROCESSED_DATA.long_field_names_map)
        }
        flowFile = session.putAllAttributes(flowFile, ATTRMAP)  # noqa
        # # REL_SUCCESS is provided by the NiFi ExecuteScript context
        session.transfer(flowFile, REL_SUCCESS)  # noqa