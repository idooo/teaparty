#!/usr/bin/python

from src import CloudWatchHelper

cw = CloudWatchHelper()
metrics = cw.getMetrics('UsedSpacePercent', 'System/Linux')

print metrics