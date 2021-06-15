import sys
import re

def removeLinesWith(lines, removekeys):
  ret = [];
  for line in lines:
    if any(k in line for k in removekeys): continue
    else: ret.append(line)
  return ret;

def deleteFromLines(lines, deletekeys):
  ret = []
  for line in lines:
    for k in deletekeys: 
      line = re.sub(k, '', line)
    ret.append(line)
  return ret

if __name__ == '__main__':
  filename = sys.argv[1]
  output = sys.argv[2]
  with open(filename) as f:
    mapperfile = removeLinesWith(f, ['name', 'sync', 'subscribe', 'who', 'BEGIN', 'unmapped'])
    mapperfile = deleteFromLines(mapperfile, ['"','\/T-Stick\.Soprano\.1','\/NI_MassiveSynth\.1','T-Stick\.1','NI_MassiveSynth\.1'])
    with open(output, 'x') as out:
      for line in mapperfile: print(line, end='', file=out)
