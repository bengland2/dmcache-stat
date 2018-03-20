# dmcache-stat

dmcache-stat.py contains a class to generate meaningful statistics from dm-cache volume counters.  If you run it as a python program, it will function like iostat and poll whatever dm-cache volumes are on the system to generate stats for as many iterations as you want.    It can output in either .csv format (default) or JSON format (with env. var. OUTPUT_JSON=1)

# class methods

* constructor has no parameters
* **parse_dmsetup_status**(text_record) - parses all fields in a **dmsetup status** record for a dm-cache
volume, converting counters into integer fields within this sample object
* **compute_rates**(previous_sample, time_difference) - compute statistics from
  this sample and the previous sample given a time difference between them.
* **stats2csv**() - outputs all fields in this sample as a CSV (comma-separated
  value) string
* **stats2json**() - outputs all fields as a python dictionary that can be converted to JSON using json.dumps()

# statistic definitions

The definitions of the fields output by stats2csv or stats2json are provided here:

* **mdblk_rate** - rate in blocks/sec at which metadata device blocks 
are being consumed (freed if negative)
* **used_cblk_rate** - rate in blocks/sec at which fast device (cache) blocks are being
  consumed (or freed if negative)
* **rd_hit_rate** - rate in hits/sec at which dm-cache is getting cache hits for
  this volume
* **wr_hit_rate** - rate in hits/sec at which dm-cache is getting cache hits for
  this volume
* **demotion_rate** - rate in blocks/sec at which dm-cache is demoting blocks from
  fast to slow device
* **promotion_rate** - rate in blocks/sec at which dm-cache is promoting blocks from
  slow to fast device
* **dirty_rate** - rate in blocks/sec at which dm-cache is adding/removing dirty
  blocks
* **rd_efficiency** - fraction of block read accesses that result in cache hits 
(0.0 to 1.0)
* **wr_efficiency** - fraction of block write accesses that result in cache hits
(0.0 to 1.0)

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


```
# OUTPUT_JSON=1 ./dmcache_stat.py 3 2
{
  "vol_info":     {
        "vg_bene-lv": {
            "policy": "2048", 
            "mode": "metadata2", 
            "sizeGB": 3
        }
    }
, "vol_samples": [
        {
            "wr_efficiency": "0.0", 
            "used_cblk_rate": "0.0", 
            "mdblk_rate": "0.0", 
            "wr_hit_rate": "0.0", 
            "promotion_rate": "0.0", 
            "demotion_rate": "0.0", 
            "rd_hit_rate": "0.0", 
            "rd_efficiency": "0.0", 
            "dirty_rate": "0.0", 
            "id": "vg_bene-lv"
        },
        {
            "wr_efficiency": "0.0", 
            "used_cblk_rate": "0.0", 
            "mdblk_rate": "0.0", 
            "wr_hit_rate": "0.0", 
            "promotion_rate": "0.0", 
            "demotion_rate": "0.0", 
            "rd_hit_rate": "0.0", 
            "rd_efficiency": "0.0", 
            "dirty_rate": "0.0", 
            "id": "vg_bene-lv"
        }
  ]
}
```
