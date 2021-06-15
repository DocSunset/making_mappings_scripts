
from mapperparse import *
from mappings import *
from bokeh.plotting import figure, output_file, show
from bokeh.models import FactorRange
from bokeh.io import export_png
from bokeh.layouts import gridplot
from math import pi
import sys

def barchart(source, x_range, y_range, ylabel, title, filename):
  for k in x:
    if k not in x_range: x_range.append(k)
  top = [pair[0] for pair in vals]


if __name__ == '__main__':
  files = sys.argv[1:]
  kbars = {}
  rbars = {}
  abars = {}
  for filename in files:
    participant = re.search('P\d+(-\d)?', filename)[0]
    print(participant)
    d = MapperData(filename)
    k = Mapping(d.finalmapsids)
    r = Mapping([m for m in d.mapgroups if m not in d.finalmapsids])
    a = Mapping(list(d.mapgroups.keys()))

    for s in SOURCES:
      if s not in kbars: kbars[s] = 0
      kbars[s] += k.sum(s)
    for s in DESTINATIONS:
      if s not in kbars: kbars[s] = 0
      kbars[s] += k.sum(s)

  output_file('charts/usage.html')
  y_range = (0, max( [kbars[s] for s in kbars]))
  x_range = [('source', s[2:-2]) for s in SOURCES]\
          + [('destination', d) for d in DESTINATIONS]

  x = []
  tops = []
  for k in kbars:
    mid_type = 'source' if k in SOURCES else 'destination'
    bot_type = k[2:-2] if k in SOURCES else k
    x.append( (mid_type, bot_type) )
    tops.append(kbars[k])

  p = figure( y_axis_label='number of times signal was tried'
            , x_axis_label=None
            , y_range=y_range
            , x_range=FactorRange(*x_range)
            , height=600
            , width =1800
            , toolbar_location=None
            , title='signal usage'
            )
  p.vbar( x=x
        , top=tops
        , width=0.6
        )
  p.xaxis.major_label_orientation = pi/4
  export_png(p)
  show(p)

