# how long do participants take after making a mapping before deciding to remove
# it?

from mapperparse import *
from bokeh.plotting import figure, output_file, show
from bokeh.transform import jitter
import re
import sys
import numpy as np

diffs = []
alldiffs = []
count = 0
files = sys.argv[1:]
for filename in files:
  mapperfile = open(filename)
  mapmessages = messagesFromOSCDumpStrings(mapperfile)
  endoftime = mapmessages[-1].timetag
  acts = mapActionsFromMessages(mapmessages)
  ids = uniqueMapIds(acts)
  maps = [a for a in acts 
      if a.type == MapAction.Type.Connect or a.type == MapAction.Type.Disconnect]
  mapgroups = groupMapMessages(ids, maps)
  closeMapGroups(mapgroups, endoftime+30)

  for k in mapgroups:
    for i, m in enumerate(mapgroups[k]):
      if m.type == MapAction.Type.Disconnect:
        mprev = mapgroups[k][i-1]
        assert(mprev.type == MapAction.Type.Connect)
        diff = m.timetag - mprev.timetag
        if m.timetag < endoftime:
          diffs.append(diff)
        alldiffs.append(diff)

N = len(alldiffs)
diffs = np.array(diffs)
alldiffs = np.array(alldiffs)
durations = np.linspace(alldiffs.min(), alldiffs.max(), N)
rejectchance = [np.count_nonzero(diffs <= T)/N for T in durations]

output_file('charts/rejectiontime_histo.html')
p = figure( x_axis_label='time spent with the mapping (s)'
          , y_axis_label='% chance the mapping was rejected'
          , height=600
          , width=600
          , toolbar_location=None
          )
p.vbar( x=durations
      , top=rejectchance
      , width=1
      )
show(p)
