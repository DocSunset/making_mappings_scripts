from mapperparse import *
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, output_file, show
import sys

# parse mapperdata
filename = sys.argv[1]
d = MapperData(filename, adjusttime=True)

# make bars from mapping actions
bars = {'y': [], 'left': [], 'right': [], 'height': [], 'color': []}
for k in d.mapgroups:
  for a in d.mapgroups[k]:
    if a.type == MapAction.Type.Connect:
      bars['left'].append(a.timetag)
      bars['y'].append(a.id())
    elif a.type == MapAction.Type.Disconnect:
      bars['right'].append(a.timetag)
      bars['height'].append(0.2)
      if a.id() in d.finalmapsids:
        bars['color'].append('blue')
      else:
        bars['color'].append('red')


# draw a line through consecutive actions
line = {'x': [], 'y': []}
for a in d.acts:
  line['x'].append(a.timetag)
  line['y'].append(a.id())

# make dots from map modifies
dots = {'x': [], 'y': []}
for a in d.modifies:
  dots['x'].append(a.timetag)
  dots['y'].append(a.id())

# plot it
d.ids.reverse()
output_file('charts/'+filename+'.timeline.html')
p = figure( x_axis_label='time (s)'
          , x_range=[0, d.endoftimeline]
          , y_axis_label='src-dst'
          , y_range=d.ids
          , sizing_mode='stretch_both'
          , toolbar_location='below'
          , toolbar_sticky=False
          , tools=['xpan', 'xwheel_zoom', 'crosshair', 'hover', 'reset']
          , active_scroll='xwheel_zoom'
          )

p.hbar(y='y', left='left', right='right', height='height', color='color',
    alpha=0.5, source=bars);
p.circle(dots['x'], dots['y'], size=10, color='cyan')
p.line(line['x'], line['y'], color='grey')
show(p)


