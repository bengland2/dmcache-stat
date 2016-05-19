# dmcache-stat

dmcache-stat.py contains a class to generate meaningful statistics from dm-cache volume counters.  If you run it as a python program, it will function like iostat and poll whatever dm-cache volumes are on the system to generate stats for as many iterations as you want.  

# standalone program usage

For example:

    # ./dmcache-stat.py
    ERROR: not enough command line parameters
    usage: dmcache-stat.py poll-interval-seconds poll-count
 
    # ./dmcache-stat.py 3 2
    [root@gprfs041-10ge ~]# ./dmcache_stat.py 2 1
    volname, size(GiB), policy, mode
    vg_ceph_osds_sdb-cachelv,   917.000, writeback, smq
    vg_ceph_osds_sdc-cachelv,   917.000, writeback, smq
    time, devname, mdblk-rate, used-cblk-rate, rd-hit-rate, wr-hit-rate, demote-rate, promote-rate, dirty-rate, rd-efficiency, wr-efficiency
    2.007587, vg_ceph_osds_sdb-cachelv, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, -36.500000, 0.000000, 0.000000
    2.007618, vg_ceph_osds_sdc-cachelv, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, -40.500000, 0.000000, 0.000000

# class methods

* - constructor has no parameters
* __str__  - converts it to a raw string for debugging purposes
* **parse_dmsetup_status**(text_record) - parses all fields in a **dmsetup status** record for a dm-cache
volume, converting counters into integer fields within this sample object
* **stats2csv**() - outputs all fields in this sample as a CSV (comma-separated
  value) string
* **compute_rates**(previous_sample, time_difference) - compute statistics from
  this sample and the previous sample given a time difference between them.
 * previous_sample - instance of this class
 * time_difference - floating-point seconds

# statistic definitions

* mdblk-rate - rate in blocks/sec at which metadata device blocks 
are being consumed (freed if negative)
* used-cblk-rate - rate in blocks/sec at which fast device blocks are being
  consumed (or freed if negative)
* rd-hit-rate - rate in hits/sec at which dm-cache is getting cache hits for
  this volume
* wr-hit-rate - rate in hits/sec at which dm-cache is getting cache hits for
  this volume
* demote-rate - rate in blocks/sec at which dm-cache is demoting blocks from
  fast to slow device
* promote-rate - rate in blocks/sec at which dm-cache is promoting blocks from
  slow to fast device
* dirty-rate - rate in blocks/sec at which dm-cache is adding/removing dirty
  blocks
* rd-efficiency - fraction of block read accesses that result in cache hits 
(0.0 to 1.0)
* wr-efficiency - fraction of block write accesses that result in cache hits
(0.0 to 1.0)


