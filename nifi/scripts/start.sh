#!/bin/bash

cp /config/libs/* lib/ &&
cp /config/scripts/preload.sh ./ &&
bash preload.sh init &&
cd /opt/nifi/nifi-current &&
../scripts/start.sh
