#!/usr/bin/python
'''
Author: Cristian Andrei Calin <cristi.calin@orange.com>

usage: remap.py [-h] -i INPUT -m MAP [-o {json,yaml}]

Remap values inside a structured file.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file
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
This program does a remapping of values in structured files (json, yaml).
- loads the file
- loads a remapping file
- applies the remapping
- prints the remapped object to standard output in the requested format
'''
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Remap values inside a structured file.')
  parser.add_argument('-i', '--input', required=True, type=argparse.FileType('r'), help='Input file')
  parser.add_argument('-m', '--map', required=True, type=argparse.FileType('r'), help='Remapping file')
  parser.add_argument('-o', '--output', required=False, choices=['json', 'yaml'], help='Output format')
  args = parser.parse_args()
  infile = parse(args.input)
  if args.map is not None:
    mapping = parse(args.map)
    outfile = do_remapping(infile, mapping)
  output_format = args.input.name.split(".")[-1]
  if args.output is not None:
    output_format = args.output
  if output_format == 'yaml':
    print yaml.dump(outfile, indent=2, default_flow_style=False)
  else:
    print json.dumps(outfile, indent=2, ensure_ascii=True)
