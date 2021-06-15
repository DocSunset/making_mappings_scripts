from mapperparse import *
from bokeh.plotting import figure, output_file, show
from bokeh.models import Span
from bokeh.layouts import gridplot
from bokeh.io import export_png
from math import log as ln
import sys

participant = sys.argv[1]
filename = participant + ".mapperdata.txt"

rawfile = 'mapperdata/orig/' + filename
f = [l for l in open(rawfile)]
firstmess = f[1] # because f[0] is BEGIN EXPERIMENT --- etc.
firstmess = messageFromOSCDumpString(firstmess)
firstmesstime = firstmess.timetag

cleanfile = 'mapperdata/' + filename
d = MapperData(cleanfile)

spans = []
connects = {'x': [], 'y': [], 'color': []}
disconns = {'x': [], 'y': [], 'color': []}
modifies = {'x': [], 'y': [], 'color': []}

class Dummy:
  def __init__(self, tt):
    self.timetag = tt

p = Dummy(firstmesstime - 0.016666667)

miny = 0
maxy = 0
for i, a in enumerate(d.acts):
  if a.timetag == p.timetag: continue
  x = (a.timetag - firstmesstime) / 60
  #y = ln((a.timetag - p.timetag)/ 60)
  y = (a.timetag - p.timetag)/ 60
  if y < miny: miny = y
  if y > maxy: maxy = y
  color = 'blue' if a.id() in d.finalmapsids else 'red'
  if a.is_connect():
    connects['x'].append(x)
    connects['y'].append(y)
    connects['color'].append(color)
  elif a.is_disconnect():
    disconns['x'].append(x)
    disconns['y'].append(y)
    disconns['color'].append(color)
  else:
    modifies['x'].append(x)
    modifies['y'].append(y)
    modifies['color'].append('cyan')
  spans.append(Span( location=x
                   , dimension='height'
                   , line_color='grey'
                   , line_dash='solid'
                   , line_width=1))
  p = a

output_name = 'charts/inter-activity period/'+filename
output_file(output_name+'.html')

p = figure( x_axis_label='time (minutes)'
          , y_axis_label='period since previous action (minutes)'
          #, y_axis_label='period since previous action (ln(minutes))'
          , x_range=[0,60]
          , y_range=[0, 8.5]
          #, y_range=[miny,maxy]
          , sizing_mode='stretch_both'
          , tools=['ypan', 'crosshair', 'hover', 'ywheel_zoom']
          , active_scroll='ywheel_zoom'
          , title='All actions'
          )

p.square( x='x'
        , y='y'
        , color='color'
        , source=connects
        , size=15
        , alpha=0.5
        )

p.diamond( x='x'
         , y='y'
         , color='color'
         , source=disconns
         , size=15
         , alpha=0.5
         )

p.circle( x='x'
        , y='y'
        , color='color'
        , source=modifies
        , size=15
        , alpha=0.5
        )

for s in spans: p.add_layout(s)

show(p)
export_png(p, output_name+'.png')
