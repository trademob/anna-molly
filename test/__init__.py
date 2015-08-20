'''
    Package level test initialization
'''

import os
import sure
import sys

from mock import Mock

ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(ROOT_DIR)

# mock the config
from fixtures import config
from lib.modules import config as config_loader

def load_config(filename):
  name = os.path.basename(filename)
  if name == 'analyzer.json':
    return config.analyzer
  elif name == 'collector.json':
    return config.collector
  elif name == 'services.json':
    return config.services
  else:
    raise Exception('No such config {}'.format(name))

orig_load = config_loader.load

# we need to mock the load function already here, so we dont need to wrap import statements in the test files
config_loader.load = Mock(side_effect=load_config)

def teardown():
  '''called when all tests of the package are done'''
  config_loader.load = orig_load
