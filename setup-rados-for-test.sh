#!/bin/bash
MON=cephmon2
RGW=gprfc073

KEYRING=/root/ceph-ansible/fetch/1956b8cc-1cc4-45d5-b9f6-be96fb776087/etc/ceph/ceph.client.admin.keyring

ansible -m copy -a "src=$KEYRING dest=/etc/ceph/ceph.client.admin.keyring" all
ansible -a "service ceph-radosgw stop" rgws

radosgw_pools=".rgw.buckets .rgw.root .rgw.control .rgw .rgw.gc .users.swift .users.uid .users .rgw.buckets.index"
for p in $radosgw_pools ; do 
  ssh $MON "rados rmpool $p $p --yes-i-really-really-mean-it"
done
#ssh $MON ceph osd erasure-code-profile rm k-10-m-2
#ssh $MON ceph osd erasure-code-profile set k-10-m-2 ruleset-failure-domain=osd k=10 m=2
#ssh $MON ceph osd crush rule rm too-few-hosts
#ssh $MON ceph osd crush rule create-erasure too-few-hosts k-10-m-2 
#sleep 5
#ssh $MON ceph osd pool create  .rgw.buckets 32 32 erasure k-10-m-2 too-few-hosts
sleep 5
ssh $MON ceph osd pool create  .rgw.buckets 1600 1600
ssh $MON ceph osd pool create .rgw.buckets.index 256 256
sleep 20
#ssh $MON ceph osd pool set .rgw.buckets pg_num 256
#sleep 20
#ssh $MON ceph osd pool set .rgw.buckets pgp_num 256
sleep 5
(ssh $MON ceph -s | grep HEALTH_OK) || \
  ( echo CLUSTER IS NOT WORKING ; exit 1 )

ansible -a "service ceph-radosgw start" rgws

sleep 5

ssh $RGW 'radosgw-admin user create --uid="testuser" --display-name="First User"'
ssh $RGW 'radosgw-admin subuser create --uid=testuser --subuser=testuser:swift --access=full'
ssh $RGW 'radosgw-admin user modify --uid=testuser --key-type=s3 --access-key=ben --secret=foobar'
ssh $RGW 'radosgw-admin key create  --subuser=testuser:swift --key-type=swift --secret=foobar'

bash wait-for-pool-cleanup.sh
cd ceph-ansible
ansible-playbook -v trim.yml

