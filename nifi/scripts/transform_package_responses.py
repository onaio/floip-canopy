"""
Transforms flow results format data from Ona API and creates a flattened
list of submissions as a dictionary.
"""
import json
import re
JYTHON_AVAILABLE = True

try:
    # This is used in the NiFi ExecuteScript context
    import java.io  # pylint: disable=unused-import
    from java.nio.charset import StandardCharsets
    from org.apache.commons.io import IOUtils
    from org.apache.nifi.processor.io import StreamCallback
except ImportError:
    JYTHON_AVAILABLE = False
    print "Skipping Jython imports"

# pylint: disable = redefined-outer-name
def transform_package_responses(data, submission_id, long_field_names_map):
    """
    Funtion to format flow results package data to flattened JSON for each
    submission and return a list of dictionaries.
    """
    transformed_data = {"submission_uuid": submission_id}

    for i in data:
        transformed_data[long_field_names_map.get(i[4]) or i[4]] = i[5]

    return transformed_data

if JYTHON_AVAILABLE:
    # pylint:disable=too-few-public-methods,invalid-name,no-self-use
    class PyStreamCallback(StreamCallback):
        """
        Class to handle flowFile stream maninpulation.
        """
        def __init__(self):
            pass

        def process(self, inputStream, outputStream):  # noqa
            """
            Takes a flowfile as an input and outputs the transform flowfile
            """
            text = IOUtils.toString(inputStream, StandardCharsets.UTF_8)  # noqa
            data = json.loads("[{}]".format(text))
            transformed_data = transform_package_responses(data,
                                                      submission_id,
                                                      long_field_names_map)

            outputStream.write(
                bytearray(json.dumps(transformed_data, indent=4).
                          encode('utf-8')))

    # session is provided by the NiFi ExecuteScript context
    # pylint:disable=undefined-variable
    flowFile = session.get()  # noqa

    if flowFile is not None:
        long_field_names_map = json.loads(
            flowFile.getAttribute("long_field_names_map"))
        submission_id = flowFile.getAttribute("submission_id")
        flowFile = session.putAttribute(flowFile, 'Content-Type',
                                        'application/json')
        flowFile = session.putAttribute(flowFile, 'mime.type',
                                        'application/json')
        session.write(flowFile, PyStreamCallback())
        session.transfer(flowFile, REL_SUCCESS)  # noqa