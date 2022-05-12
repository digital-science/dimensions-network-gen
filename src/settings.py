#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Settings for dim-networkgen module
"""

import os


# locations

HERE = os.path.abspath(__file__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(HERE))  # one level above 'networkgen' folder

PROJECT_STATIC_FOLDER =  PROJECT_ROOT + "/src/static" 
DEFAULT_OUTPUT_LOCATION = PROJECT_ROOT + "/user-outputs"
DEFAULT_OUTPUT_NETWORKS = DEFAULT_OUTPUT_LOCATION + "/networks"
DEFAULT_NETWORK_INIT = PROJECT_ROOT + "/src/networkgen/config_default.ini"


# network visualizations tasks available

TASKS = ['collab_orgs', 'concepts']

