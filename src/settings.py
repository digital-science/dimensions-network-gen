#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Settings for networkgen module
"""

import os


# locations

HERE = os.path.abspath(__file__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(HERE))  # one level above 'networkgen' folder
# PROJECT_SRC = PROJECT_ROOT + "/src"

# print(f'DEBUG: PROJECT_ROOT: {PROJECT_ROOT}')

PROJECT_STATIC_FOLDER =  PROJECT_ROOT + "/src/static" 

DEFAULT_INPUT_LOCATION = PROJECT_ROOT + "/user-inputs"
DEFAULT_OUTPUT_LOCATION = PROJECT_ROOT + "/user-outputs"
DEFAULT_OUTPUT_NETWORKS = DEFAULT_OUTPUT_LOCATION + "/networks"

DEFAULT_NETWORK_INIT = PROJECT_ROOT + "/src/networkgen/config_default.ini"


# covid/dimensions dataset selection

if True:
    DIMENSIONS_DATASET = "covid-19-dimensions-ai.data"
else:
    DIMENSIONS_DATASET = "dimensions-ai.data_analytics"



# tasks

TASKS = ['collab_orgs', 'concepts']
# TASKS = ['concepts', 'collab_orgs', 'collab_authors']

