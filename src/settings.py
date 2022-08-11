#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Settings for dim-networkgen module
"""

import os


# locations

HERE = os.path.abspath(__file__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(HERE))  # one level above 'networkgen' folder

PROJECT_STATIC_PATH =  PROJECT_ROOT + "/src/static" 
DEFAULT_OUTPUT_PATH = PROJECT_ROOT + "/build"
DEFAULT_OUTPUT_JSON_PATH = DEFAULT_OUTPUT_PATH + "/json"
DEFAULT_OUTPUT_SQL_PATH = DEFAULT_OUTPUT_PATH + "/sql"

DEFAULT_NETWORK_INIT = PROJECT_ROOT + "/src/networkgen/config_default.ini"


# network visualizations tasks available
NETWORK_TYPES = ['concepts', 'organizations']

# network visualizations parameters
NETWORK_PARAMETERS_DEFAULT = {
    'network_types' : ", ".join(NETWORK_TYPES), 
    'max_nodes' : 500, 
    'min_edge_weight' : 3 ,
    'min_concept_relevance': 0.5, 
    'min_concept_frequency': 5, 
}