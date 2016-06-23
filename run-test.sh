ansible -m script -a "drop-cache.sh" osds 
./start-test.sh $*
if [ $? != 0 ] ; then exit 1 ; fi
sleep 2 
user-benchmark bash wait-for-done.sh
cp /tmp/workload.xml `ls -tdr /var/lib/pbench-agent/user* | tail -1`/
