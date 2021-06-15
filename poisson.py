import numpy as np
from mapperparse import *

def bin(d, binsize=1): # bin size in minutes
  lastbin = int(d.acts[-1].timetag / (60 * binsize))
  bins = [ [] for i in np.arange(0,60, binsize)]
  for a in d.acts:
    i = int(a.timetag / (60 * binsize))
    if (i < len(bins)): bins[i].append(a)
  return bins, lastbin

def timeplot(bins):
  return

def histoplot(bins):
  return 

if __name__ == "__main__":
  from bokeh import palettes
  from bokeh.plotting import figure, output_file, show
  from bokeh.models import Span
  from bokeh.layouts import layout
  from bokeh.io import export_png
  from scipy.special import factorial
  import sys
  participants = sys.argv[1:]

  output_name = 'charts/poisson'
  output_file(output_name+'.html')

  bar_width = 0.7
  timeline_width = 1000
  binsizes = [0.5, 1, 2, 4, 8]
  palette = palettes.Category10[len(binsizes)]

  layouts = []
  orates = []
  for p in participants:
    filename = p + ".mapperdata.txt"
    rawfile = 'mapperdata/orig/' + filename
    f = [l for l in open(rawfile)]
    firstmess = f[1] # because f[0] is BEGIN EXPERIMENT --- etc.
    firstmess = messageFromOSCDumpString(firstmess)
    firstmesstime = firstmess.timetag
    
    cleanfile = 'mapperdata/' + filename
    d = MapperData(cleanfile)

    for a in d.acts:
      a.timetag = a.timetag - firstmesstime

    rates = {'x': [], 'y': [], 'color': []}
    for i, t in enumerate(binsizes):
      timelinefig = figure( 
            title=f'{p}, interval = {t} minutes'
          , x_axis_label = 'time (minutes)'
          , y_axis_label = 'number of changes to mapping'
          , x_range=[0,60]
          #, y_range should be set when we know the overall max
          , tools=['xpan', 'crosshair', 'hover', 'xwheel_zoom']
          , active_scroll='xwheel_zoom'
          , plot_width=timeline_width
          , plot_height=500
          )
      distributionfig = figure( 
            title=f'{p} "number of changes" distribution, interval = {t} minutes'
          , x_axis_label = 'number of changes in interval (k)'
          , y_axis_label = 'number of occurrences of k changes'
          , tools=['crosshair', 'hover']
          , plot_height=500
          )
      # fig.orientation = 'vertical'

      bins, lastbin = bin(d, t)
      changes = [len(b) for i, b in enumerate(bins) if i <= lastbin]
      distrib = [changes.count(k) for k in set(changes)]
      lambba = np.mean(changes)
      rates['x'].append(t)
      rates['y'].append(lambba / t )
      if i == 1: orates.append(lambba / (60*t) )
      rates['color'].append(palette[i])
      timelinefig.vbar(
            x = [(j+0.5) * t for j, _ in enumerate(changes)]
          , top = changes
          , color=palette[i]
          , width=bar_width
          )
      distributionfig.vbar(
            x = [k for k in set(changes)]
          , top = distrib
          , color=palette[i]
          , width=bar_width
          )
      x = np.linspace(0, max(changes), 32)
      k = np.arange(0,max(changes)+1)
      yx = (np.float_power(lambba, x) * np.exp(-lambba) / factorial(x))
      yk = (np.float_power(lambba, k) * np.exp(-lambba) / factorial(k)) 
      distributionfig.line(
            line_dash='dashed'
          , x = x
          , y = max(distrib) * yx / np.max(yx)
          , color = 'black'
          , alpha = 0.3
          , line_width = 2
          )
      distributionfig.circle(
            x = k
          , y = max(distrib) * yk / np.max(yk)
          , color = 'black'
          , alpha = 1
          , size = 5
          )

      layouts.append([timelinefig, distributionfig])

    ratesfig = figure(
          title=f'{p} average rate vs interval duration'
        , x_axis_label='interval duration (minutes)'
        , y_axis_label='average rate (changes / minute)'
        , plot_height=500
        )
    ratesfig.vbar(
          x = 'x'
        , top = 'y'
        , source = rates
        , width=bar_width
        )
    layouts.append([ratesfig])

  overall_rates = figure(
        title = 'estimated activity rate by participant'
      , x_range = participants
      , x_axis_label = 'participant'
      , y_axis_label = 'changes / minute'
      , plot_height = 500
      )
  overall_rates.vbar(
        x = participants
      , top = orates
      , width = bar_width
      )
  layouts.append(overall_rates)
  p = layout(layouts)
  show(p)
