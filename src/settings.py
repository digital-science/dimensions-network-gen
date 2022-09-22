#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Settings for dimensions-networks module
"""

import os


# locations

HERE = os.path.abspath(__file__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(HERE))  # one level above 'networkgen' folder

PROJECT_STATIC_PATH =  PROJECT_ROOT + "/src/html" 
DEFAULT_TOPICS_SQL_PATH = PROJECT_ROOT + "/topics"
DEFAULT_TOPICS_JSON_PATH = DEFAULT_TOPICS_SQL_PATH + "/json"

DEFAULT_BUILD_PATH = PROJECT_ROOT + "/build"
DEFAULT_BUILD_TOPICS_PATH = DEFAULT_BUILD_PATH + "/topics"

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


BASE_DIMENSIONS_URL = """https://app.dimensions.ai/discover/publication?search_text=%222019-nCoV%22%20OR%20%22COVID-19%22%20OR%20%E2%80%9CSARS-CoV-2%E2%80%9D%20OR%20%22HCoV-2019%22%20OR%20%22hcov%22%20OR%20%22NCOVID-19%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20coronavirus%202%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20corona%20virus%202%22%20OR%20%E2%80%9Ccoronavirus%20disease%202019%E2%80%9D%20OR%20((%22coronavirus%22%20OR%20%22corona%20virus%22)%20AND%20(Wuhan%20OR%20China%20OR%20novel)){custom_search}&search_type=kws&search_field=full_search&search_mode=content&or_facet_year=2022&or_facet_year=2021&or_facet_year=2020"""