#!/bin/bash -x
# input units are MB
dev=$1
parts=$2
lvmpv_sz=$3
ceph_journal_sz=$4
if [ -z "$ceph_journal_sz" ] ; then exit 1 ; fi 
partprobe $dev

delay()
{
  echo 'import time; time.sleep(0.2)' | python
}

b=1
for p in `seq 1 $parts` ; do 
  (( e = $b + $lvmpv_sz )) 
  delay
  (parted -s -a optimal $dev mkpart logical ${b}M ${e}M && \
   parted -s $dev name $p lvm_pv_$p) || exit 1
  (( b = $b + $lvmpv_sz ))
done
for p in `seq 1 $parts` ; do
  (( partnum = $p + $parts ))
  (( e = $b + $ceph_journal_sz ))
  delay
  (parted -s -a optimal $dev mkpart logical ${b}M ${e}M && \
   parted -s $dev name $partnum ceph_journal_$p) || exit 1
  (( b = $b + $ceph_journal_sz ))
done
partprobe $dev
