import xml.etree.ElementTree as ET
import re
import sys
import argparse as ap

KEEP = False
REMOVE = True
textpatt = re.compile('\S.*')
spacepatt = re.compile('((\ \ \ \ )+\n)|(\n)')
def prune(xmlelem, parentaltags, matches, andmode=False):
  tags = parentaltags + [xmlelem.tag]
  if (andmode and set(matches).issubset(tags))\
      or (not andmode and xmlelem.tag in matches):
    return KEEP
  elif len(xmlelem) == 0:
    return REMOVE
  else:
    if xmlelem.text: 
      xmlelem.text = textpatt.sub('', xmlelem.text)
      xmlelem.text = spacepatt.sub('', xmlelem.text)
      xmlelem.text = '\n' + xmlelem.text
    if xmlelem.tail: 
      xmlelem.tail = textpatt.sub('', xmlelem.tail)
      xmlelem.tail = spacepatt.sub('', xmlelem.tail)
      xmlelem.tail = '\n\n' + xmlelem.tail

    ret = REMOVE
    for child in list(xmlelem):
      if prune(child, tags, matches, andmode) is REMOVE:
        xmlelem.remove(child)
      else:
        ret = KEEP

    return ret

def scrape(xmlelem, rootname, data):
  if len(xmlelem) == 0:
    if xmlelem.tag not in data.keys():
      data[xmlelem.tag] = { rootname: 1 }
    elif rootname not in data[xmlelem.tag]:
      data[xmlelem.tag][rootname] = 1
    else:
      data[xmlelem.tag][rootname] += 1
    return
  for child in list(xmlelem):
    scrape(child, rootname, data)

def main():
  parser = ap.ArgumentParser(description="a simple utility to extract certain tags from an xml file")
  parser.add_argument("-a", "--and", action="store_true", default=False, required=False,
      dest="and", help="switch from default inclusive or to and mode")
  parser.add_argument("-t", "--tag", action="append", required=False, dest="tags",
      help="an xml tag which should be preserved in the output, e.g. '-t a'. Any number can be specified")
  parser.add_argument("files", nargs="+", 
      help="files from which to extract the specified tags")

  args = vars(parser.parse_args())
  files = args["files"]
  tags = args["tags"]
  andmode = args["and"]
  if tags:
    filter_tags(files, tags, andmode)
  else:
    return scrape_tags(files)

def get_root(filename):
  tree = ET.ElementTree()
  try:
    tree.parse(filename)
  except ET.ParseError as e:
    print("{} parse failed: {}, {}".format(filename, e.code, e.position))
    return False
  except FileNotFoundError:
    print("{} not found".format(filename))
    return False
  return tree.getroot()

def filter_tags(files, tags, andmode):
  participant_count = 0
  quotation_count = 0
  for filename in files:
    root = get_root(filename)
    if root is False:
      continue

    print('################')
    prune(root, [], tags, andmode)
    ET.dump(root)
    if len(root) > 0: 
      participant_count = participant_count + 1
      for t in tags:
        quotation_count = quotation_count + len(root.findall(".//"+t))
    print('') # add a new line to the output

  print('participant count: ', participant_count)
  print('quotation count:   ', quotation_count)

def scrape_tags(files):
  data = dict()
  for filename in files:
    root = get_root(filename)
    if root is False:
      continue
    scrape(root, root.tag, data)
  for k, v in data.items():
    print (f"{k:10} {len(v.keys()):3} {v}")
  return data

if __name__ == "__main__":
  out = main()
