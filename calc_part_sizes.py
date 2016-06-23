#!/usr/bin/python
from sys import argv

# units should be MB

# convert to MiB for LVM

MiB_per_MB = 1/1.024/1.024

fastdev_size = int(argv[1])
slowdevs = int(argv[2])
ssd_journal_size = int(argv[3])
fs_journal_size = int(argv[4])
metalv_size = int(argv[5])
size_per_slow_dev = (fastdev_size - 1000.0) / slowdevs
total_per_osd_fast_size = size_per_slow_dev - (ssd_journal_size + 500)
fs_journal_size /= MiB_per_MB
metalv_size /= MiB_per_MB
fastlv_size = total_per_osd_fast_size - (metalv_size + fs_journal_size + 500)
fastlv_size *= MiB_per_MB
print('%d' % int(total_per_osd_fast_size))
print('%d' % int(fastlv_size))
