from bokeh.plotting import figure
from bokeh.transform import jitter

def cat_dots_plot(categories, dots, title, color='blue', toolbar=None):
  p = figure( x_axis_label='participant ID'
            , x_range=categories
            , y_axis_label='duration (s)'
            , height=600
            , width=600
            , toolbar_location=toolbar
            , tools=['ypan', 'crosshair', 'hover', 'ywheel_zoom']
            , active_scroll='ywheel_zoom'
            , title=title
            )
  p.circle( x=jitter('x', width=0.6, range=p.x_range)
          , y='y'
          , color=color
          , source=dots
          , size=15
          , alpha=0.1
          )
  return p

def make_round_to_nearest(m):
  return lambda n: int(m) if n <= m else int(((n // m) + 1) * m)

def duration_histo_plot(yr, durs, binsize, color):
  rounder = make_round_to_nearest(binsize)
  mind = min(durs)
  maxd = max(durs)
  y = list(range(rounder(mind), rounder(maxd), binsize))
  rounded = [rounder(d) for d in durs]
  right = [rounded.count(n) for n in y]
  p = figure( x_axis_label='number of mappings'
            , y_axis_label='duration (s) [binsize='+str(binsize)+'s]'
            , y_range=yr
            , height=600
            , width=300
            , toolbar_location=None
            , tools=['ypan', 'crosshair', 'hover', 'ywheel_zoom']
            , active_scroll='ywheel_zoom'
            )
  p.hbar( y=y
        , height=10
        , right=right
        , color=color
        , alpha=0.5
        )
  return p
