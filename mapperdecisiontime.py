# how long do participants take after making a mapping before deciding to remove
# it?

from mapperparse import *
from bokeh.plotting import figure, output_file, show
from bokeh.transform import jitter
from bokeh.layouts import row
from bokeh.io import export_png
import re
import sys
import numpy as np

groupname = 'group'
participants = [groupname]
tdots = {'x': [], 'y': [], 'color': []}
kdots = {'x': [], 'y': [], 'color': []}
rdots = {'x': [], 'y': [], 'color': []}
files = sys.argv[1:]
for filename in files:
  participant = re.search('P\d+', filename)[0]
  participants.append(participant)
  d = MapperData(filename)

  for k in d.mapgroups:
    for i, m in enumerate(d.mapgroups[k]):
      if m.type == MapAction.Type.Disconnect:
        mprev = d.mapgroups[k][i-1]
        assert(mprev.type == MapAction.Type.Connect)
        diff = m.timetag - mprev.timetag
        if m.id() in d.finalmapsids and m.timetag < d.endoftime: # accepted eventually
          tdots['x'].append(participant)
          tdots['y'].append(diff)
          tdots['x'].append(groupname)
          tdots['y'].append(diff)
          tdots['color'].append('blue')
          tdots['color'].append('blue')
        elif m.timetag >= d.endoftime: # accepted finally
          kdots['x'].append(participant)
          kdots['y'].append(diff)
          kdots['x'].append(groupname)
          kdots['y'].append(diff)
          kdots['color'].append('green')
          kdots['color'].append('green')
        else:
          rdots['x'].append(participant)
          rdots['y'].append(diff)
          rdots['x'].append(groupname)
          rdots['y'].append(diff)
          rdots['color'].append('red')
          rdots['color'].append('red')

participants = sorted(list(set(participants)))
output_name = 'charts/rejectiontime'
output_file(output_name+'.html')

def plot(dots, title):
  p = figure( x_axis_label='participant ID'
            , x_range=participants
            , y_axis_label='duration of an active mapping (s)'
            , height=600
            , width=600
            , toolbar_location=None
            , title=title
            )
  p.circle( x=jitter('x', width=0.45, range=p.x_range)
          , y='y'
          , color='color'
          , source=dots
          , size=15
          , alpha=0.1
          )
  return p

layout = row( plot(kdots, 'final mappings')
            , plot(tdots, 'tested mappings')
            , plot(rdots, 'rejected mappings')
            )
show(layout)
export_png(layout, output_name+'.png')

print('final mappings: {}, tested mappings: {}, rejected mappings: {}'.format(
    len(kdots['y']), len(tdots['y']), len(rdots['y'])))
