#!/bin/bash

export NIFI_BASE_URL="http://nifi:8080"
export WORKING_DIR="/config/nifi/scripts/"
export NIFI_VERSION="1.9.2"
export password="p@ssw0rd"
export NIFI_UP_RETRY_COUNT=240

main() {
  if waitNifiAvailable ${NIFI_UP_RETRY_COUNT}; then
    local subCommand=$1

    if [ "$subCommand" == "init" ]; then
      initialize "${@:2}"
    else
      return 1
    fi
  else
    return 1
  fi

  return $?
}

waitNifiAvailable() {
  echo "Waiting for NiFi to be available"
  local maxTries=$1
  local retryCount=1

  while ! curl -f "$NIFI_BASE_URL/nifi"; do
    sleep 10
    retryCount=$((retryCount + 1))
    if [[ "$retryCount" -gt "$maxTries" ]]; then
      return 1
    fi
  done

  return 0
}

initialize() {
  startFlows "$@"
}

startFlows() {
  sleep 100
  echo "Starting flows"
  # Check if template has been added to canvas
  templates=$(curl http://nifi:8080/nifi-api/flow/templates | jq ".templates")
  if [ "$templates"  == "[]" ] ;
  then 
    # Upload template and add it to canvas
    curl -X POST -F template=@"/config/template/flow_results.xml" $NIFI_BASE_URL/nifi-api/process-groups/root/templates/upload
    uploadedTemplateId=$(curl http://nifi:8080/nifi-api/flow/templates | jq ".templates[0].id" -r)
    curl -X POST -H "Content-Type:application/json" $NIFI_BASE_URL/nifi-api/process-groups/root/template-instance -d '{"originX": 2.0,"originY": 3.0,"templateId": "'"$uploadedTemplateId"'"}' | jq ".flow.processGroups[0].id" -r
    processorGroupId=$(curl -X GET $NIFI_BASE_URL/nifi-api/process-groups/root/process-groups | jq ".processGroups[0].id" -r)

    # Set DB password and start service
    controllerServiceId=$(curl -X GET $NIFI_BASE_URL/nifi-api/flow/process-groups/$processorGroupId/controller-services | jq ".controllerServices[0].id" -r)
    curl -X PUT -H 'Content-Type: application/json' -d '{"revision":{"clientId":"random", "version":"0"},"component":{"id":"'"${controllerServiceId}"'","properties":{"Password":"p@ssw0rd"}}}' $NIFI_BASE_URL/nifi-api/controller-services/${controllerServiceId}
    curl -X PUT -H 'Content-Type: application/json' -d '{"revision":{"clientId":"random", "version":"0"},"component":{"id":"'"${controllerServiceId}"'","state":"ENABLED"}}' $NIFI_BASE_URL/nifi-api/controller-services/${controllerServiceId}

    sleep 5
    # Start the process group
    curl -X PUT -H 'Content-Type: application/json' -d '{"id":"'"${processorGroupId}"'","state":"RUNNING"}' $NIFI_BASE_URL/nifi-api/flow/process-groups/${processorGroupId}
    fi
}

main "$@" &
exit $?