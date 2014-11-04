#!/usr/bin/python

import sys
import yaml
import json

if __name__ == '__main__':
  content = json.load(sys.stdin)
  print yaml.dump(content, indent=2, default_flow_style=False)

