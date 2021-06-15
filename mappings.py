# what mappings did participants make? what mappings did they try and reject?
from mapperparse import *
from bokeh.models import BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
from bokeh.plotting import figure, output_file, show
from bokeh.transform import transform
from bokeh.palettes import Viridis256, linear_palette
import colorcet as cc
from bokeh.io import export_png
import sys
import numpy as np

SOURCES =      [ "['/brush']"
               , "['/eggbeater']"
               , "['/hold']"
               , "['/jab']"
               , "['/rub']"
               , "['/shake']"
               , "['/squeez']"
               , "['/tilt']"
               , "['/touch']"
               ]

DESTINATIONS = [ "/amp"
               , "/feedback"
               , "/filter/cutoff"
               , "/filter/resonance"
               , "/noise/amp"
               , "/noise/color"
               , "/pitch"
               , "/reverb"
               , "/waveform"
               ]

CONNECTIONS = []
for s in reversed(SOURCES):
  for d in reversed(DESTINATIONS):
    CONNECTIONS.append(s+'->'+d)

class Mapping:
  def __init__(self, connections=[]):
    self.mapping = {c: 0 for c in CONNECTIONS}
    self.add_connections(connections)

  def add_connections(self, connections):
    self.modify_connections(connections, 1)

  def remove_connections(self, connections):
    self.modify_connections(connections, -1)

  def modify_connections(self, connections, modifier):
    for c in connections:
      if c in self.mapping:
        self.mapping[c] += modifier

  def to_columns(self):
    cols = {'srcs': [], 'dsts': [], 'vals': self.vals()}
    for m in self.mapping:
      split = m.split('->')
      cols['srcs'].append(split[0][2:-2])
      cols['dsts'].append(split[1])
    return cols

  def from_columns(self, cols):
    self.__init__()
    mappings = []
    for s, d, v in zip(cols['srcs'], cols['dsts'], cols['vals']):
      i = "['"+s+"']->"+d
      if i in self.mapping:
        self.mapping[i] = v
    return self

  def to_np_array(self):
    cols = self.to_columns()
    return np.array(list(reversed(cols['vals']))).reshape((len(DESTINATIONS), len(SOURCES)))

  def from_np_array(self, arr):
    vals = list(reversed(arr.reshape(len(DESTINATIONS)*len(SOURCES))))
    cols = self.to_columns()
    cols['vals'] = vals
    self.from_columns(cols)

  def vals(self):
    return [self.mapping[m] for m in self.mapping]

  def min(self):
    return min(self.vals())

  def max(self):
    return max(self.vals())

  def sum(self, key):
    ret = 0
    ret += sum([self.mapping[k] for k in self.mapping if key in k])
    return ret

  def plot(self, title='mapping', filename='mapping.png', palette=Viridis256):
    m = self
    colormap = LinearColorMapper(palette=linear_palette(palette,
      (m.max()-m.min())+1)
                                , low=m.min(), high=m.max()
                                )
    c = m.to_columns()
    f = figure( y_axis_label='source'
              , x_axis_label='destination'
              , y_range=list(reversed(sorted(list(set(c['srcs'])))))
              , x_range=sorted(list(set(c['dsts'])))
              , height=800
              , width =800
              , toolbar_location=None
              , title=title
              )
    f.rect(x="dsts"
          , y="srcs"
          , width=0.98
          , height=0.98
          , source=c
          , line_color=None
          , fill_color=transform('vals', colormap)
          )
    colorbar = ColorBar(color_mapper=colormap
                       , location=(0, 0)
                       , ticker=BasicTicker(desired_num_ticks=m.max())
                       , formatter=PrintfTickFormatter(format="%d")) 
    f.add_layout(colorbar, 'right')
    export_png(f, filename=filename)

if __name__ == '__main__':
  files = sys.argv[1:]

  gkmap = Mapping()
  print('checking Mapping files')
  for filename in filter(lambda f: 'mapping' in f, files):
    print(filename)
    participant = re.search('P\d+(-\d)?', filename)[0]
    print(participant)
    d = MapperDataJson(filename)
    m = Mapping(d.finalmapsids)
    gkmap.add_connections(d.finalmapsids)
    m.plot( participant+' mapping'
          , 'charts/mappings/'+participant+'.finalmapping.png'
          , Viridis256
          )

  if sum(gkmap.vals()) > 0: 
    gkmap.plot('all mappings'
              , 'charts/mappings/group.finalmapping.png'
              , Viridis256
              )

  grmap = Mapping()
  print('checking mapper data files')
  for filename in filter(lambda f: 'mapperdata' in f, files):
    participant = re.search('P\d+(-\d)?', filename)[0]
    print(participant)
    d = MapperData(filename)
    ids = [m for m in d.mapgroups if m not in d.finalmapsids]
    m = Mapping(ids)
    grmap.add_connections(ids)
    m.plot( participant+' rejected mappings'
          , 'charts/mappings/'+participant+'.rejectedmappings.png'
          , cc.kr
          )

  if sum(grmap.vals()) > 0: 
    grmap.plot('all rejected mappings'
              , 'charts/mappings/group.rejectedmappings.png'
              , cc.fire[0:-10]
              )

  if sum(grmap.vals()) > 0 and sum(gkmap.vals()) > 0:
    kvals = gkmap.vals()
    rvals = grmap.vals()
    totalvals = [k + r for k, r in zip(kvals, rvals)]
    combinedvals = [k - r for k, r in zip(kvals, rvals)]
    controversy  = [min([k, r]) for k, r in zip(kvals, rvals)]
    totalcols = gkmap.to_columns()
    totalcols['vals'] = totalvals
    combinedcols = gkmap.to_columns()
    combinedcols['vals'] = combinedvals
    controversycols = gkmap.to_columns()
    controversycols['vals'] = controversy
    gtmap = Mapping().from_columns(totalcols)
    gtmap.plot('cumulative all mappings tested'
              , 'charts/mappings/group.totalmappingstested.png'
              , Viridis256
              )
    gcmap = Mapping().from_columns(combinedcols)
    gcmap.plot('accepted mappings minus rejected mappings'
              , 'charts/mappings/group.combinedmappings.png'
              , cc.bky
              )
    gcsmap = Mapping().from_columns(controversycols)
    gcsmap.plot('mapping controversy score'
              , 'charts/mappings/group.controversymappings.png'
              , Viridis256
              )



