#!/bin/bash
objects_per_container=$1
prepare_or_read=$2
obj_size_kb=$3
workers=$4
if [ -z "$workers" ] ; then workers=64 ; fi
if [ "$obj_size_kb" = "" ] ; then
  echo "usage: start-test.sh objects-per-container prepare-or-read object-size-kb worker-threads"
  exit 1
fi
(( total_objs = $objects_per_container * 100 ))
workload="workload-config-$prepare_or_read.xml"
sed "s/_OBJS_PER_CONTAINER_/$objects_per_container/" < $workload \
 | sed "s/_TOTAL_OBJS_/$total_objs/" \
 | sed "s/_OBJ_SIZE_/$obj_size_kb/g" \
 | sed "s/_WORKERS_/$workers/" > /tmp/workload.xml
cd /root/cosbench/0.4.2.c3
bash cli.sh submit /tmp/workload.xml

