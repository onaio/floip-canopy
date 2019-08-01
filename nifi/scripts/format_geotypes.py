import json

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


def format_geotypes(data, geopoints):
    if any(geopoints):
        geopoints_set_intersection = set(data) & set(geopoints)
        for e in geopoints_set_intersection:
            data["_{}_latitude".format(e)] = data[e].split()[0]
            data["_{}_longitude".format(e)] = data[e].split()[1]
            data["_{}_altitude".format(e)] = float(data[e].split(" ")[2])
            data["_{}_accuracy".format(e)] = float(data[e].split(" ")[3])
            del data[e]
    return data


if jython_available:

    class PyStreamCallback(StreamCallback):
        def __init__(self):
            pass

        def process(self, inputStream, outputStream):
            text = IOUtils.toString(inputStream, StandardCharsets.UTF_8)
            obj = json.loads(text)

            data = format_geotypes(obj, GEOPOINTS)
            outputStream.write(
                bytearray(json.dumps(data, indent=4).encode('utf-8')))

    # session is provided by the NiFi ExecuteScript context
    flowFile = session.get()  # noqa
    if flowFile is not None:
        GEOPOINTS = json.loads(flowFile.getAttribute('geopoints'))

        flowFile = session.write(flowFile, PyStreamCallback())  # noqa
        # REL_SUCCESS is provided by the NiFi ExecuteScript context
        session.transfer(flowFile, REL_SUCCESS)  # noqa