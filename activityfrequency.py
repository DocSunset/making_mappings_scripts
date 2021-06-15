# is there any consistency in the frequency of mapper actions?
# e.g. connections and modifications in particular

from mapperparse import *
from plotters import *
from bokeh.plotting import figure, output_file, show
from bokeh.transform import jitter
from bokeh.layouts import gridplot
from bokeh.io import export_png
import sys

groupname = 'group'
participants = [groupname]
cdots = {'x': [], 'y': []}
cdiffs = []
mdots = {'x': [], 'y': []}
mdiffs = []
adots = {'x': [], 'y': []}
adiffs = []
files = sys.argv[1:]
for filename in files:
  participant = re.search('P\d+', filename)[0]
  participants.append(participant)
  d = MapperData(filename)

  connects = [a for a in d.acts if a.is_connect()]
  for a, b in zip(connects, connects[1:]):
    diff = b.timetag - a.timetag
    cdots['x'].append(participant)
    cdots['y'].append(diff)
    cdots['x'].append(groupname)
    cdots['y'].append(diff)
    cdiffs.append(diff)

  modifies = [a for a in d.acts if a.is_modify()]
  for a, b in zip(modifies, modifies[1:]):
    diff = b.timetag - a.timetag
    mdots['x'].append(participant)
    mdots['y'].append(diff)
    mdots['x'].append(groupname)
    mdots['y'].append(diff)
    mdiffs.append(diff)

  acts = d.acts
  for a, b in zip(acts, acts[1:]):
    diff = b.timetag - a.timetag
    adots['x'].append(participant)
    adots['y'].append(diff)
    adots['x'].append(groupname)
    adots['y'].append(diff)
    adiffs.append(diff)

participants = sorted(list(set(participants)))
output_name = 'charts/activityfrequency'
output_file(output_name+'.html')

def plot(dots, title, color):
  p = figure( x_axis_label='participant ID'
            , x_range=participants
            , y_axis_label='period between actions (s)'
            , height=600
            , width=600
            , toolbar_location='below'
            , tools=['crosshair', 'ywheel_zoom']
            , title=title
            )
  p.circle( x=jitter('x', width=0.7, range=p.x_range)
          , y='y'
          , source=dots
          , size=15
          , alpha=0.1
          , color=color
          )
  return p

ccolor = 'blue'
mcolor = 'red'
acolor = 'green'
p1 = cat_dots_plot(participants, cdots, 'connections', ccolor)
p2 = duration_histo_plot(None, cdiffs, 20, ccolor)
p3 = cat_dots_plot(participants, mdots, 'modifications', mcolor)
p4 = duration_histo_plot(None, mdiffs, 20, mcolor)
p5 = cat_dots_plot(participants, adots, 'all changes', acolor)
p6 = duration_histo_plot(None, adiffs, 20, acolor)

layout = gridplot([[p1, p2],[p3,p4], [p5,p6]])
show(layout)
export_png(layout, output_name+'.png')
