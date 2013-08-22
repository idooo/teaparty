#!/usr/bin/python

from src import CloudWatchHelper, DBAdapter

cw = CloudWatchHelper()
metrics = cw.getMetrics('UsedSpacePercent', 'System/Linux')

print metrics

db = DBAdapter('db/test.db')