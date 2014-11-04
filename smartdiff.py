#!/usr/bin/python
'''
Author: Cristian Andrei Calin <cristi.calin@orange.com>

usage: smartdiff.py [-h] -f FIRST -s SECOND [-r REGEX [REGEX ...]] [-m MAP]
                    [-o {json,yaml}]

Compute a difference between serialized files.

optional arguments:
  -h, --help            show this help message and exit
  -f FIRST, --first FIRST
                        First file to compare
  -s SECOND, --second SECOND
                        Second file to compate
  -r REGEX [REGEX ...], --regex REGEX [REGEX ...]
                        Regular expression to filter on
  -m MAP, --map MAP     Remapping file
  -o {json,yaml}, --output {json,yaml}
                        Output format

'''

import re
import json
import yaml
import argparse
import json_tools

'''
Parse a file and deduce the format based on the file extension
Input:
  f - file descriptor of the file to be parsed
Output:
  the map resulted from loading the file
'''
def parse(f):
  p = f.name.split(".")
  exec "result = %s.load(f)" % p[1]
  return result

'''
Pluck function used in a filter() call to remove values that are not of interest.
This is implemented as a decorator to simplify the logic and not use global variables.
Input:
  param - the object to check
Output:
  true - keep
  false - remove
'''
def pluck(parm):

  def apply_filter(element):
    string = None
    if "replace" in element:
      string = element["replace"]
    if "add" in element:
      string = element["add"]
    if "remove" in element:
      string = element["remove"]
    if string is not None:
      if re.search(parm, string) is not None:
        return False
    return True

  return apply_filter

'''
Remap specific values before doing a diff, this is to prevent useless output
Input:
  obj - the map to parse
  mapping - the mapping to apply
Output:
  the remapped object
'''
def do_remapping(obj, mapping):
  for mapping_node in mapping["paths"]:
    path = json_tools.path.resolve(obj, mapping_node["path"])
    for path_node in path:
      for field in mapping_node["fields"]:
        for remap in mapping_node["map"]:
          new = re.sub(r"\b%s\b" % (remap), mapping_node["map"][remap], path_node[field])
          if new != path_node[field]:
            path_node[field] = new
    if mapping_node["sort"]:
      path.sort(key=lambda node: node[mapping_node["sort_key"]])
  return obj

'''
This program does a "smart" diff of structured files (yaml or json).
- loads the files
- applies a remapping to the first file to avoid false pozitives
- does a diff between the files
- plucks out uninteresting differences
- displays the resulted diff in the requested format
'''
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Compute a difference between serialized files.')
  parser.add_argument('-f', '--first', required=True, type=argparse.FileType('r'), help='First file to compare')
  parser.add_argument('-s', '--second', required=True, type=argparse.FileType('r'), help='Second file to compate')
  parser.add_argument('-r', '--regex', required=False, nargs="+", help='Regular expression to filter on')
  parser.add_argument('-m', '--map', required=False, type=argparse.FileType('r'), help='Remapping file')
  parser.add_argument('-o', '--output', required=False, choices=['json', 'yaml'], default='json', help='Output format')
  args = parser.parse_args()
  first = parse(args.first)
  second = parse(args.second)
  if args.map is not None:
    mapping = parse(args.map)
    first = do_remapping(first, mapping)
  diff = json_tools.diff(first, second)
  if args.regex is not None:
    for expr in args.regex:
      diff = filter(pluck(expr), diff)
  if args.output == 'yaml':
    print yaml.dump(diff, indent=2, default_flow_style=False)
  else:
    print json.dumps(diff, indent=2, ensure_ascii=True)
