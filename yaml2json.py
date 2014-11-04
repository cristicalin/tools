#!/usr/bin/python

import sys
import yaml
import json

if __name__ == '__main__':
  content = yaml.load(sys.stdin)
  print json.dumps(content, indent=2)
  
