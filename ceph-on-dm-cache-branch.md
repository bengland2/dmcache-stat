This ceph-on-dm-cache branch is just a way of illustrating ideas presented in a
performance results document being made available to people interested in Ceph
usage of dm-cache.  This branch may go away once this material becomes stale!

If questions contact Ben England at bengland@redhat.com but this is not a
commitment to support these scripts, which were only designed to work in one
test environment and illustrate one way that Ceph-on-dm-cache could be
implemented.

To use these files, do:

    # cd
    # git clone https://github.com/ceph/ceph-ansible

Then copy these files into the top-level directory of the
ceph-ansible tree:

o trim.yml - ansible script to invoke trim.sh on OSDs
o trim.sh - shell script to run fstrim on all OSD filesystems
o dmcache.yml - ansible script for dm-cache-backed OSD directory mountpoints
o trim.sh - shell script to trim all OSDs on host
o mkpart.sh - script to construct partitions needed by dm-cache and Ceph
o calc-part-sizes.py - compute partition and LV sizes needed by Ceph + dm-cache

And copy these files into $HOME:

o run-test.sh - run an entire RGW Swift create or read workload
o setup-rados-for-test.sh - reset RGW Swift environment
o start-test.sh - start COSBench load running
o wait-for-done.sh - wait until COSBench load is done
o workload-config-prepare.xml - COSBench object create workload template
o workload-config-read.xml - COSBench object read workload template
o numa-partition-osds.sh - script to pin OSD processes to CPU sockets
