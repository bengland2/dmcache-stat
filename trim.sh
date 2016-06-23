#!/bin/bash -v

ceph osd set noout
service ceph stop
for fs in /var/lib/ceph/osd/sd* ; do 
  #eval "fstrim $fs > /tmp/fstrim-`basename $fs`.log 2>&1 &"
  fstrim $fs > /tmp/fstrim-`basename $fs`.log 2>&1
  #pids="$pids $!"
done
#for p in pids ; do wait $p ; done
service ceph start
sleep 10
ceph osd unset noout
while [ 1 ] ; do 
  ceph health | grep _OK && break
  sleep 5
done

