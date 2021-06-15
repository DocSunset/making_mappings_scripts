from mapperparse import *
from bokeh.plotting import figure, output_file, show
from bokeh.models import Span
from bokeh.layouts import gridplot
from bokeh.io import export_png
import sys
import numpy as np

times = []
participants = []
files = sys.argv[1:] # load raw mapper data files, not cleaned up
for filename in files:
  participant = re.search('P\d+(\-\d)*', filename)[0]
  participants.append(participant)
  f = [l for l in open(filename)]
  firstmess = f[1] # because f[0] is BEGIN EXPERIMENT --- etc.
  firstmess = messageFromOSCDumpString(firstmess)
  firstmesstime = firstmess.timetag
  firstmap = next((m for m in f if 'connect' in m or 'map' in m), None)
  firstmap = messageFromOSCDumpString(firstmap)
  firstmaptime = firstmap.timetag
  times.append(firstmaptime - firstmesstime)

for p, t in zip(participants, times): print(p, t)
print('average', sum(times) / len(times))
print('std', np.std(np.array(times)))

output_file('charts/learningtime.html')

p = figure( title='time from start of task to first mapping'
          , y_axis_label='time (minutes)'
          , x_axis_label='participant'
          , x_range=sorted(list(set(participants)))
          , height = 800
          , width = 800
          , toolbar_location=None
          )
p.vbar( x=participants
      , top=np.array(times) / 60
      , width=0.8
      )
avg = Span(location=np.mean(np.array(times) / 60)
          , dimension='width'
          , line_color='green'
          , line_dash='dashed'
          , line_width=3)
p.add_layout(avg)
show(p)
export_png('charts/learningtime.png')
