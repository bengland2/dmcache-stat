#!/bin/bash
cd $COSBENCH_DIR

get_active()
{
  bash cli.sh info 2>/tmp/e | awk '/active workload/{print $2}'
}

while [ 1 ] ; do
  active=`get_active`
  if [ $active = 0 ] ; then break ; fi
  sleep 5
done
echo "no active COSBench workloads"
