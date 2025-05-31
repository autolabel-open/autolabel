#!/bin/bash

set -x

declare -a scene_names=(
    # python-demoo: python
    "python-demo"

    # juice-shop: node.js
    "juice-shop"

    # gitlist: php
    "vulhub/gitlist/CVE-2018-1000533"

    # geoserver: java
    "vulhub/geoserver/CVE-2023-25157"
    "vulhub/geoserver/CVE-2024-36401"

    # adminer
    "vulhub/adminer/CVE-2021-43008"

    # metabase: java + Clojure
    "vulhub/metabase/CVE-2021-41277"
    "vulhub/metabase/CVE-2023-38646"

    # solr: java
    "vulhub/solr/CVE-2017-12629-RCE"
    "vulhub/solr/CVE-2017-12629-XXE"
    "vulhub/solr/CVE-2019-0193"
    "vulhub/solr/CVE-2019-17558"

    # cmsms: php
    "vulhub/cmsms/CVE-2019-9053"
    "vulhub/cmsms/CVE-2021-26120-lab"

    # ofbiz: java
    "vulhub/ofbiz/CVE-2020-9496"
    "vulhub/ofbiz/CVE-2023-49070"
    "vulhub/ofbiz/CVE-2024-38856"
    "vulhub/ofbiz/CVE-2024-45195"
    "vulhub/ofbiz/CVE-2024-45507"
    "vulhub/ofbiz/CVE-2023-51467"

    # joomla: php
    "vulhub/joomla/CVE-2015-8562"
    "vulhub/joomla/CVE-2017-8917"
    "vulhub/joomla/CVE-2023-23752"

    # mongo-express: node.js
    "vulhub/mongo-express/CVE-2019-10758"

    # kibana: node.js
    "vulhub/kibana/CVE-2018-17246"

    # pgadmin: python
    "vulhub/pgadmin/CVE-2022-4223"
    "vulhub/pgadmin/CVE-2023-5002"

    # sandworm
    "sandworm"

    # multi-jump
    "multi-jump"
)

RUN_TIMES=1

for TIMES in $(seq 1 $RUN_TIMES); do
  echo "Current Run: ${TIMES}"
  for scene_name in "${scene_names[@]}"; do
      echo "Building ${scene_name}⏩"
      time BATCH=1 poetry run python main.py --config-path example/${scene_name} --output-path results/${scene_name}
      echo "Finished build ${scene_name}🎉"
  done
done
