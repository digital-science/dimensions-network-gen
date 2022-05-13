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

NETWORK_TYPES = ['collab_orgs', 'concepts']

# network visualizations parameters

NETWORK_PARAMETERS_DEFAULT = {
    'network_types' : ", ".join(NETWORK_TYPES), 
    'max_nodes' : 500, 
    'min_edge_weight' : 3 ,
    'min_concept_relevance': 0.5, 
    'min_concept_frequency': 5, 
}