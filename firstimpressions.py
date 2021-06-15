# is the theme of the importance of 1st impressions present in the usage data?
# for instance, how many times do participants try a mapping before deciding
# whether to accept or reject it? What total amount of time do they spend?

from plotters import *
from mapperparse import *
from bokeh.plotting import figure, output_file, show
from bokeh.transform import jitter
from bokeh.layouts import layout
from bokeh.io import export_png
import sys
import numpy as np

groupname = 'group'
participants = [groupname]
kdurs = []
rdurs = []
kdots = {'x': [], 'y': []}
rdots = {'x': [], 'y': []}
kcounts = {}
rcounts = {}
files = sys.argv[1:]

all_maps = 0
kept_maps = 0
rejected_maps = 0
connections_count = 0
all_keeps_count = 0
all_rejects_count = 0
for filename in files:
  participant = re.search('P\d+', filename)[0]
  participants.append(participant)
  d = MapperData(filename)

  for k in d.mapgroups:
    all_maps += 1
    dur = 0
    tries = 0
    for i, m in enumerate(d.mapgroups[k]):
      if m.type == MapAction.Type.Disconnect:
        mprev = d.mapgroups[k][i-1]
        assert(mprev.type == MapAction.Type.Connect)
        dur += m.timetag - mprev.timetag
        tries += 1
        connections_count += 1
        if k in d.finalmapsids: all_keeps_count += 1
        else: all_rejects_count += 1

    if k in d.finalmapsids: # accepted finally
      kdurs.append(dur)
      kdots['x'].append(participant)
      kdots['y'].append(dur)
      kdots['x'].append(groupname)
      kdots['y'].append(dur)
      if kcounts.get(tries) is None: kcounts[tries] = 1
      else: kcounts[tries] = kcounts[tries] + 1
      kept_maps += 1
    else:
      rdurs.append(dur)
      rdots['x'].append(participant)
      rdots['y'].append(dur)
      rdots['x'].append(groupname)
      rdots['y'].append(dur)
      if rcounts.get(tries) is None: rcounts[tries] = 1
      else: rcounts[tries] = rcounts[tries] + 1
      rejected_maps += 1

assert(connections_count == all_keeps_count + all_rejects_count)
assert(all_keeps_count == sum([kcounts[k]*k for k in kcounts]))
assert(all_rejects_count == sum([rcounts[k]*k for k in rcounts]))
assert(all_maps == sum([kcounts[k] for k in kcounts] + [rcounts[k] for k in rcounts]))
print(all_maps, kept_maps, rejected_maps)
print(kcounts, rcounts)
print(f"keep stats: mean duration = {np.mean(kdots['y'])}, quartiles = {np.percentile(kdots['y'], [25, 50, 75])}")
print(f"keep stats: mean duration = {np.mean(rdots['y'])}, quartiles = {np.percentile(rdots['y'], [25, 50, 75])}")
participants = sorted(list(set(participants)))
output_name = 'charts/decisiontime'
output_file(output_name+'.html')

histomax = max([kcounts[k] for k in kcounts]+[rcounts[k] for k in rcounts])
historange = (1,histomax+10)

def trieshisto(yr, d, color):
  p = figure( x_axis_label='number of tries'
            , y_range=yr
            , y_axis_label='number of mappings'
            , height=600
            , width=600
            , toolbar_location=None
            , tools=['hover', 'crosshair', 'ywheel_zoom']
            )
  p.vbar( x=list(d.keys())
        , width=0.6
        , top=[d[k] for k in d]
        , color=color
        , alpha=0.5
        )
  return p

kcolor = 'green'
rcolor = 'red'
binsize = 20
p1 = cat_dots_plot(participants, kdots, 'accepted mappings', kcolor)
p2 = duration_histo_plot(p1.y_range, kdurs, binsize, kcolor)
p3 = cat_dots_plot(participants, rdots, 'rejected mappings', rcolor)
p4 = duration_histo_plot(p3.y_range, rdurs, binsize, rcolor)

p5 = trieshisto(historange, kcounts, kcolor)
p6 = trieshisto(historange, rcounts, rcolor)
l = layout([[p1, p2, p3, p4], [p5, p6]])
show(l)
export_png(l, output_name+'.png')
