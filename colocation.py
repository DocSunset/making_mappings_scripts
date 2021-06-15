from mappings import *
from mapperparse import *
from bokeh.models import BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
from bokeh.plotting import figure, output_file, show
from bokeh.transform import transform
from bokeh.palettes import Viridis256, linear_palette
import colorcet as cc
from bokeh.io import export_png
import sys
import numpy as np
from distutils.util import strtobool

COLOCATIONS = []
for c1 in reversed(CONNECTIONS):
  for c2 in reversed(CONNECTIONS):
    COLOCATIONS.append(c1+'&'+c2)

class MappingColocation():
  def __init__(self, mapping=Mapping()):
    self.colocation = {c: 0 for c in COLOCATIONS}
    self.add_mapping(mapping)

  def add_mapping(self, mapping):
    self.modify_mapping(mapping, 1)

  def remove_mapping(self, mapping):
    self.modify_mapping(mapping, -1)

  def modify_mapping(self, mapping, modifier):
    mapping = mapping.mapping
    for k1 in mapping:
      for k2 in mapping:
        if mapping[k1] and mapping[k2]:
          key = k1+'&'+k2 
          if key in self.colocation:
            self.colocation[key] += 1

  def vals(self):
    return [self.colocation[c] for c in self.colocation]

  def to_columns(self):
    cols = {'m1': [], 'm2': [], 'vals': self.vals()}
    for c in self.colocation:
      split = c.split('&')
      cols['m1'].append(split[0])
      cols['m2'].append(split[1])
    return cols

  def max(self):
    return max(self.vals())

  def min(self):
    return min(self.vals())

  def plot(self, title='mapping', filename='mapping.png', palette=Viridis256):
    c = self
    colormap = LinearColorMapper(palette=linear_palette(palette,
      (c.max()-c.min())+1)
                                , low=c.min(), high=c.max()
                                )
    cols = c.to_columns()
    f = figure( y_axis_label='mapping 1'
              , x_axis_label='mapping 2'
              , y_range=list(reversed(sorted(list(set(cols['m1'])))))
              , x_range=sorted(list(set(cols['m2'])))
              , height=1200
              , width =1200
              , toolbar_location=None
              , title=title
              )
    f.xaxis.major_label_orientation = 1
    f.rect(x="m1"
          , y="m2"
          , width=0.90
          , height=0.90
          , source=cols
          , line_color='grey'
          , fill_color=transform('vals', colormap)
          )
    colorbar = ColorBar(color_mapper=colormap
                       , location=(0, 0)
                       , ticker=BasicTicker(desired_num_ticks=c.max())
                       , formatter=PrintfTickFormatter(format="%d")) 
    f.add_layout(colorbar, 'right')
    export_png(f, filename)

if __name__ == '__main__':
  gc = MappingColocation()
  files = sys.argv[1:]

  for filename in files:
    participant = re.search('P\d+(-\d)?', filename)[0]
    print(participant)
    d = MapperDataJson(filename)
    m = Mapping(d.finalmapsids)
    c = MappingColocation(m)
    gc.add_mapping(m)
    c.plot(participant+' mapping colocations'
          , 'charts/mappings/colocations/'+participant+'.coloc.png'
          , Viridis256
          )
  gc.plot( 'all mappings colocations'
         , 'charts/mappings/colocations/group.coloc.png'
         , Viridis256
         )
