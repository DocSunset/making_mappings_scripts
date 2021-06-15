from mapperparse import *
import sys

accepts = 0
rejects = 0
modifies = 0
convergents = 0

files = sys.argv[1:]
for filename in files:
  participant = re.search('P\d+', filename)[0]
  d = MapperData(filename)
  modkeys = [m.id() for m in d.modifies]
  
  for k in d.mapgroups:
    accepts += 1 if k in d.finalmapsids else 0
    rejects += 1 if k not in d.finalmapsids else 0
    modifies += 1 if k in d.finalmapsids and k in modkeys else 0
    convergents += 1 if ',' in k else 0

print(  'accepts:     ', accepts, 
      '\nrejects:     ', rejects, 
      '\nmodifies:    ', modifies,
      '\nconvergents: ', convergents)
    

