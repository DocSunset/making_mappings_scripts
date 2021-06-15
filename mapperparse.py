import re
import json
import numpy as np
from enum import Enum
from mapperclean import deleteFromLines

class Message():
  def __init__(self):
    self.timetag = -1
    self.address = ''
    self.typetags = ''
    self.args = []

  def __repr__(self):
    return str((self.timetag, self.address, self.typetags, self.args))

class MapAction():
  Type = Enum('MapAction', 'Connect Disconnect Modify Undefined')

  def __init__(self, message=None):
    self.timetag = -1
    self.type = self.Type.Undefined
    self.src = []
    self.dst = ''
    if message is not None:
      self.timetag = message.timetag
      self.setTypeFromMessage(message)
      self.setIdFromMessage(message)

  def setTypeFromMessage(self, message):
    if message.address in ['/connect', '/map']:
      self.type = MapAction.Type.Connect
    elif message.address in ['/disconnect', '/unmap']:
      self.type = MapAction.Type.Disconnect
    elif message.address in ['/connection/modify', '/map/modify']:
      self.type = MapAction.Type.Modify
    else: 
      self.type = MapAction.Type.Undefined
      print("unexpected message address ", message.address)

  def setIdFromMessage(self, message):
    if 'connect' in message.address:
      self.src = [message.args[0]]
      self.dst = message.args[1]
    elif '<-' in message.args:
      self.src = [a for a in message.args[2:] if '/' == str(a)[0]]
      self.dst = message.args[0]
    elif '->' in message.args:
      idx = message.args.index('->')
      self.src = [a for a in message.args[0:idx] if '/' == str(a)[0]]
      self.dst = message.args[idx+1]
    else:
      self.src = []
      self.dst = ''
      print("unexpected message format ", message)

  def is_connect(self):
    return self.type == MapAction.Type.Connect
  def is_disconnect(self):
    return self.type == MapAction.Type.Disconnect
  def is_modify(self):
    return self.type == MapAction.Type.Modify

  def id(self):
    return str(self.src)+'->'+self.dst

  def sameEdge(self, other):
    if isinstance(other, MapAction):
      return self.id() == other.id();
    elif self.id() == other:
      return True
    else: return False

  def __hash__(self):
    return hash((self.id()))

  def __eq__(self, other):
    return self.sameEdge(other)

  def __lt__ (self, other):
    return self.timetag < other.timetag

  def __gt__(self, other):
    return self.timetag > other.timetag

  def __repr__(self):
    return str((self.timetag, self.type, self.src, self.dst))


def oscdumpTimeTagToTime(ttstring):
  ttwords = re.sub('\.', ' ', ttstring).split()
  return float(int(ttwords[0],16)*2**32 + int(ttwords[1], 16)) / 2**32

def messageFromOSCDumpString(line):
  line = re.sub("\\n", '', line)
  line = line.split(' ')
  msg = Message()
  msg.timetag = oscdumpTimeTagToTime(line[0])
  msg.address = line[1]
  msg.typetags = line[2]
  for typetag, arg in zip(line[2], line[3:]):
    if   typetag == 'f': msg.args.append(float(arg))
    elif typetag == 's': msg.args.append(str(arg))
    elif typetag == 'i': msg.args.append(int(arg))
    elif typetag == 'h': msg.args.append(int(arg))
    else: print("unexpected typetag '{}'".format(typetag))
  return msg

def messagesFromOSCDumpStrings(lines):
  ret = []
  for line in lines:
    ret.append(messageFromOSCDumpString(line))
  return ret

def mapActionsFromMessages(messages):
  return [MapAction(m) for m in messages]

def uniqueMapIds(mapacts):
  ids = []
  for a in mapacts:
    aid = a.id()
    if aid not in ids:
      ids.append(aid)
  return ids

def adjustTime(messages):
  beginningoftime = messages[0].timetag - 30
  for i, m in enumerate(messages): 
    messages[i].timetag -= beginningoftime
  endoftime = messages[-1].timetag
  return beginningoftime, endoftime

def groupMapMessages(uniquemaps, maps):
  return {u: [m for m in maps if m == u] for u in uniquemaps}

def printMapGroups(maps):
  for key in maps:
    print(key, ': ')
    for m in maps[key]:
      print('    {}'.format(m))
    print('\n')

def closeMapGroups(mapgroups, endoftime):
  finalmaps = []
  for key in mapgroups:
    if (int(len(mapgroups[key])) & 0x1) > 0:
      lastconnect = mapgroups[key][-1]
      finisher = MapAction()
      finisher.src = lastconnect.src
      finisher.dst = lastconnect.dst
      finisher.timetag = endoftime
      finisher.type = MapAction.Type.Disconnect
      mapgroups[key].append(finisher)
      finalmaps.append(lastconnect)
      if len(lastconnect.src) > 1:
        for src in lastconnect.src:
          extrafinal = MapAction()
          extrafinal.src = [src]
          extrafinal.dst = lastconnect.dst
          finalmaps.append(extrafinal)
  return uniqueMapIds(finalmaps)

class MapperData():
  def __init__(self, filename, adjusttime=False):
    mapperfile = open(filename)
    mapmessages = messagesFromOSCDumpStrings(mapperfile)
    if adjusttime:
      self.beginningoftime, self.endoftime = adjustTime(mapmessages)
    else:
      self.beginningoftime = mapmessages[0].timetag
      self.endoftime = mapmessages[-1].timetag
    self.endoftimeline = self.endoftime + 30
    self.acts = mapActionsFromMessages(mapmessages)
    self.ids = uniqueMapIds(self.acts)
    self.maps = [a for a in self.acts 
        if a.type == MapAction.Type.Connect or a.type == MapAction.Type.Disconnect]
    self.modifies = [a for a in self.acts if a.type == MapAction.Type.Modify]
    self.mapgroups = groupMapMessages(self.ids, self.maps)
    self.finalmapsids = closeMapGroups(self.mapgroups, self.endoftimeline)

class MapperDataJson():
  def __init__(self, filename):
    self.finalmapsids = []
    mapperfile = json.load(open(filename))
    if mapperfile['fileversion'] == '2.1': self.parse1(mapperfile)
    elif mapperfile['fileversion'] == '2.2': self.parse2(mapperfile)
    self.finalmapsids = deleteFromLines(self.finalmapsids
                                       , [ '\/T-Stick\.Soprano\.1'
                                         ,'\/NI_MassiveSynth\.1'
                                         ,'T-Stick\.1'
                                         ,'NI_MassiveSynth\.1'
                                         ]
                                       )

  def parse1(self, mapperfile):
    maps = mapperfile['mapping']['connections']
    for m in maps:
      src = m['src']
      dst = m['dest'][0]
      self.add_id(src, dst)

  def parse2(self, mapperfile):
    maps = mapperfile['mapping']['maps']
    for m in maps:
      srcs = [s['name'] for s in m['sources']]
      dst = m['destinations'][0]['name']
      self.add_id(srcs, dst)
      if len(srcs) > 1:
        for s in srcs:
          self.add_id([s], dst)

  def add_id(self, srcs, dst):
    i = str(srcs)+'->'+dst
    self.finalmapsids.append(i)
