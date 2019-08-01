import json
import re
from datetime import datetime

jython_available = True

try:
    # This is used in the NiFi ExecuteScript context
    import java.io  # noqa
    from org.apache.commons.io import IOUtils
    from java.nio.charset import StandardCharsets
    from org.apache.nifi.processor.io import StreamCallback
except ImportError:
    jython_available = False
    print("Skipping Jython imports")

FINAL_LIST = []
# UNWANTED_CHARACTERS = "-(),.:;'[]?/\|{}?><!@#$%^&*+ "
# IGNORED_LIST = ["_notes", "_tags", "_attachments", "_geolocation"]

datetime_format_regex = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
datetimezone_format_regex =\
    re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+\W+\d{2}:*\d*')


def remove_special_characters(name):
    name = re.sub(r"[-\\\(\),\.:;'\[\]\?\/\|{}\?><!@#\$%\^&\*\+ ]", '_', name)
    return name


def underscore_to_slash(x): 
    return x.replace('_', '/')

def slash_to_underscore(x):
    return x.replace('/','_')


def replace_metadata_column_name(k, metadata_details):
    for key in METADATA_DETAILS_KEYS:
        if k == underscore_to_slash(metadata_details["%s_field_name" %key]):
            return key

def flatten_nested_json(data):
    new_dict = {}
    new_list = []

    # metadata_column_names = map(lambda x: underscore_to_slash(x),
    #                             metadata_details.values())
    for k, v in data.items():
        # k = long_field_names.get(slash_to_underscore(k)) or k
        # if isinstance(v, list) and k not in IGNORED_LIST:
        if isinstance(v, list):
            new_list = new_list + v
        # elif k in metadata_column_names:
        #     metadata_type = replace_metadata_column_name(k, metadata_details)
        #     new_dict[metadata_type] = \
        #         reformat_timestamps(v) if isinstance(v, unicode) else v
        # elif k not in IGNORED_LIST:
        else:
            # k = slash_to_underscore(k)
            # k = remove_unwanted_characters(k).lower()
            new_dict[k] = \
                reformat_timestamps(v) if isinstance(v, unicode) else v

    if len(new_list) > 0:
        for i in new_list:
            new_i = {}
            for key, value in i.iteritems():
                # key = slash_to_underscore(key)
                key = remove_special_characters(key).lower()
                new_i[key] = \
                    reformat_timestamps(value) if isinstance(value, unicode) else value
            new_i.update(new_dict)
            if len({k: v for k, v in new_i.iteritems() \
                if isinstance(v, list)}) > 0:
                flatten_nested_json(new_i)
            else:
                FINAL_LIST.append(new_i)
    else:
        FINAL_LIST.append(new_dict)
    return FINAL_LIST


def reformat_timestamps(value):
    formats = ('%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d')
    timestamps_pattern = re.compile(r'\d+\/\d+\/\d+[\d+\w+\s+:.]*')
    if timestamps_pattern.match(value):
        date_time_list = re.split('T|\s', value)
        date_value = date_time_list[0]
        time_value = ''
        if len(date_time_list) > 1:
            if re.match('\d+:\d+:\d+.\d+', date_time_list[1]):
                time_value = date_time_list[1].split('+')[0]
            elif re.match('\d+:\d+:\d+', date_time_list[1]):
                time_value = date_time_list[1] + '.000'

        for format in formats:
            matched = get_date_format(date_value, format)
            if matched == False:
                get_date_format(date_value, format)
            else:
                new_date = datetime.strptime(date_value, format)
                formatted_data = new_date.strftime('%Y-%m-%d') + ' ' + time_value 
    elif datetimezone_format_regex.match(value):
        formatted_data = value.replace('T', ' ').split('+')[0]
    elif datetime_format_regex.match(value):
        formatted_data = value.replace('T', ' ').decode('utf8') + ".000"
    else:
        formatted_data = value
    return formatted_data

def get_date_format(date_value, format):
    correct_format = False
    try:
        datetime.strptime(date_value, format)
        correct_format = True
    except ValueError:
        correct_format = False
    
    return correct_format


if jython_available:

    class PyStreamCallback(StreamCallback):

        def __init__(self):
            pass

        def process(self, inputStream, outputStream):
            text = IOUtils.toString(inputStream, StandardCharsets.UTF_8)
            obj = json.loads(text)
            flattened_data = flatten_nested_json(obj)

            outputStream.write(bytearray(json.dumps(
                flattened_data, indent=4).encode('utf-8')))

    # session is provided by the NiFi ExecuteScript context
    flowFile = session.get()  # noqa
    if flowFile is not None:
        # metadata_details = json.loads(flowFile.getAttribute(
        #     'metadata_details'))
        # long_field_names_map = json.loads(flowFile.getAttribute(
        #     'long_field_names_map'))

        flowFile = session.write(flowFile, PyStreamCallback())  # noqa
        # REL_SUCCESS is provided by the NiFi ExecuteScript context
        session.transfer(flowFile, REL_SUCCESS)  # noqa
