#!/usr/bin/python
#
# dmcache_stat.py - script to compute useful statistics from 
# dmsetup status counters for dmcache volumes
# to run:
#   python dmcache_stat.py 2 3
# this will generate 3 samples of stats.  Each round of stats will have
# a 2-second measurement interval
# or use it as a class to parse log files that already exist.
#
# This script outputs in .csv format so that data can be directly loaded
# into a spreadsheet.  It could easily output in JSON format as well 
# if this would be useful.
#

import subprocess
import time
import sys
import os

SECTORS_PER_KB = 2
KB_PER_GiB = 1024 * 1024

# representation of integer fields in dmsetup status output,
# along with statistics computed from those fields,
# for a single dm-cache volume

class dmcache_vol_sample:
    def __init__(self):

        # input fields from dmcache status

        self.id = ''
        self.md_blksz = 0
        self.used_mdblks = 0
        self.total_mdblks = 0
        self.cache_blksz_kb = 0
        self.used_cblks = 0
        self.total_cblks = 0
        self.rd_hits = self.rd_misses = self.wr_hits = self.wr_misses = 0
        self.demotions = self.promotions = self.dirty = 0
        self.volsize = 0.0
        self.mode = None
        self.policy = None

        # output stats

        # for blocks/sec consumed, negative number means blocks/sec freed
        self.mdblk_rate = 0.0         # metadata blocks/sec consumed
        self.used_cblk_rate = 0.0     # cache blocks/sec consumed
        self.rd_hit_rate = 0.0        # read hits/sec
        self.rd_miss_rate = 0.0       # read cache misses/sec
        self.wr_hit_rate = 0.0        # write hits/sec
        self.wr_miss_rate = 0.0       # write misses/sec
        self.demotion_rate = 0.0      # demotions/sec
        self.promotion_rate = 0.0     # promotions/sec
        self.dirty_rate = 0.0         # rate of change in dirty blocks
        # cache efficiency is measured as hits/(hits+misses), [0.0,1.0]
        self.rd_efficiency = 0.0      # read efficiency
        self.wr_efficiency = 0.0      # write efficiency 

    # dump object in string format

    def __str__(self):
        samp = ('%s blksz %d used_mdblks %d total_mdblks %d cache_blksz_kb %d '+
                'used_cblks %d total_cblks %d rd_hits %d rd_misses %d ' + 
                'wr_hits %d wr_misses %d ' + 
                'demotions %d promotions %d dirty %d ' + 
                'volsize %f mode %s policy %s ') % (
               self.id, self.md_blksz, self.used_mdblks, self.total_mdblks,
               self.cache_blksz_kb, self.used_cblks, self.total_cblks,
               self.rd_hits, self.rd_misses, self.wr_hits, self.wr_misses,
               self.demotions, self.promotions, self.dirty, 
               self.volsize, self.mode, self.policy)
        stats = ('mdblk_rate %f used_cblk_rate %f ' + 
                 'rd_hit_rate %f rd_miss_rate %f ' + 
                 'wr_hit_rate %f wr_miss_rate %f ' + 
                 'demotion_rate %f promotion_rate %f dirty_rate %f ' +
                 'rd_efficiency %f wr_efficiency %f ') % (
                 self.mdblk_rate, self.used_cblk_rate, 
                 self.rd_hit_rate, self.rd_miss_rate, 
                 self.wr_hit_rate, self.wr_miss_rate,
                 self.demotion_rate, self.promotion_rate, self.dirty_rate,
                 self.rd_efficiency, self.wr_efficiency)
        return samp + stats

    # compute rate and efficiency statistics from list of per-volume counters
 
    def compute_rates(self, s1, poll_interval):
        self.mdblk_rate = (self.used_mdblks - s1.used_mdblks)/poll_interval
        self.used_cblk_rate = (self.used_cblks - s1.used_cblks)/poll_interval
        self.rd_hit_rate = (self.rd_hits - s1.rd_hits)/poll_interval
        self.rd_miss_rate = (self.rd_misses - s1.rd_misses)/poll_interval
        self.wr_hit_rate = (self.wr_hits - s1.wr_hits)/poll_interval
        self.wr_miss_rate = (self.wr_misses - s1.wr_misses)/poll_interval
        self.demotion_rate = (self.demotions - s1.demotions)/poll_interval
        self.promotion_rate = (self.promotions - s1.promotions)/poll_interval
        self.dirty_rate = (self.dirty - s1.dirty)/poll_interval
        self.rd_efficiency = 0.0
        if (self.rd_miss_rate + self.rd_hit_rate) > 0.0:
            self.rd_efficiency = float(self.rd_hit_rate) / (
                                     self.rd_miss_rate + self.rd_hit_rate)
        self.wr_efficiency = 0.0
        if (self.wr_hit_rate + self.wr_miss_rate) > 0.0:
            self.wr_efficiency = float(self.wr_hit_rate) / (
                                     self.wr_hit_rate + self.wr_miss_rate)

    # convert computed stats to CSV format

    def stats2csv(self):
        d = self
        return '%s, %f, %f, %f, %f, %f, %f, %f, %f, %f' % (
               d.id, d.mdblk_rate, d.used_cblk_rate, 
               d.rd_hit_rate, d.wr_hit_rate,
               d.demotion_rate, d.promotion_rate, d.dirty_rate,
               d.rd_efficiency, d.wr_efficiency)

    # convert token of form "a/b" to a 2-tuple of numbers

    def split_pair(self, pair_token):
        pair = pair_token.split('/')
        return (int(pair[0]), int(pair[1]))

    # given a dmsetup status record for a dm-cache volume, 
    # parse it into a dmcache_sample object
    # the format is documented in 
    # https://www.kernel.org/doc/Documentation/device-mapper/cache.txt

    def parse_dmsetup_status(self, text_record):
        tkns = text_record.split()

        volname = tkns[0].split(':')[0]
        vol_mode = tkns[16]
        vol_policy = tkns[20]

        self.id = tkns[0].split(':')[0]

        # parse the configuration parameters for this volume

        vol_size_sectors = int(tkns[2])
        self.volsize = vol_size_sectors / SECTORS_PER_KB / KB_PER_GiB
        self.mode = tkns[16]
        self.policy = tkns[20]

        # parse the counters for this volume

        self.md_blksz = int(tkns[4])
        (self.used_mdblks, self.total_mdblks) = self.split_pair(tkns[5])
        self.cache_blksz_kb = int(tkns[6])/SECTORS_PER_KB
        (self.used_cblks, self.total_cblks) = self.split_pair(tkns[7])
        self.rd_hits = int(tkns[8])
        self.rd_misses = int(tkns[9])
        self.wr_hits = int(tkns[10])
        self.wr_misses = int(tkns[11])
        self.demotions = int(tkns[12])
        self.promotions = int(tkns[13])
        self.dirty = int(tkns[14])


# MAIN PROGRAM
# if you run this program, it will attempt to function standalone, more like
# iostat.  But you can call into the class to manipulate dmcache counter
# data from any source

def extract_vol_id( v ):
    return v.id

# convert dmsetup status records for dm-cache volumes to 
# list of structure consisting of counters and config parameters

def poll_dmcache():
    dmsetup_out = subprocess.check_output(['dmsetup', 'status']) 
    dmsetup_lines = dmsetup_out.split('\n')
    dmcache_lines = []
    for l in dmsetup_lines:
        if os.getenv('DEBUG'): print l
        tkns = l.strip().split()
	if len(tkns) == 0: continue
        if tkns[3] == 'cache': dmcache_lines.append(l)
    dmcache_raw = []
    for l in dmcache_lines:
        rec = dmcache_vol_sample()
        rec.parse_dmsetup_status(l)
        dmcache_raw.append(rec)
    return sorted(dmcache_raw, key=extract_vol_id)

def usage(msg):
    print('ERROR: ' + msg)
    print('usage: dmcache-stat.py poll-interval-seconds poll-count')
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 3: usage('not enough command line parameters')
    poll_interval = float(sys.argv[1])
    poll_count = int(sys.argv[2])

    print('volname, size(GiB), policy, mode')
    s2 = poll_dmcache()
    for v in s2:
        print('%s, %9.3f, %s, %s' % (
            v.id, v.volsize, v.mode, v.policy))
    print('')

    base_time = time.time()
    for p in range(0, poll_count):
        time.sleep(poll_interval)
        s1 = s2
        s2 = poll_dmcache()
        # compute stats for this interval
        if os.getenv('DEBUG'):
            for v in s2: 
                print time.time(), v
        print('time, devname, mdblk-rate, used-cblk-rate, rd-hit-rate, wr-hit-rate, demote-rate, promote-rate, dirty-rate, rd-efficiency, wr-efficiency')
        for j in range(0, len(s2)): 
            s2[j].compute_rates(s1[j], poll_interval)
            delta_time = time.time() - base_time
            print('%f, %s' % (delta_time, s2[j].stats2csv()))
        print('')

