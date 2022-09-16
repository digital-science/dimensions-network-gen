#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import click

from .settings import *
from .networkgen.helpers import *
from .networkgen.networkgen import * 
from .networkgen.vosviewer import *
from .networkgen import server as run_server 



@click.command()
@click.argument('filename', nargs=-1)
@click.option(
    "--buildindex", "-i",
    is_flag=True,
    help="Just build the index page listing out previously created networks.")
@click.option(
    "--fulldimensions", "-f",
    is_flag=True,
    help="Query using the full Dimensions dataset, instead of the COVID19 subset (note: requires subscription).")
@click.option(
    "--keyword", "-k",
    help="Generate a keyword-search SQL query and run it.")
@click.option(
    "--runserver", "-r",
    is_flag=True,
    help="Run the webserver.")
@click.option(
    "--port", "-p", default=8009,
    help="Specify the port on which the webserver should listen for connections (default: 8009).")
@click.option('--verbose', is_flag=True, help='Verbose mode')
@click.pass_context
def main_cli(ctx, filename=None,  
                verbose=False, 
                buildindex=False, 
                fulldimensions=False, 
                keyword=None, 
                runserver=False, 
                port=None,):
    """dim-networkgen: a tool for creating network visualizations powered by data from Dimensions on Google BigQuery. Example: 

dim-networkgen {QUERY_FILE}

QUERY_FILE. File name containing the GBQ query to be converted into a network. If a folder is passed, all files in the folder will be processed.     
"""

    if not filename and not runserver and not buildindex and not keyword:
        # print dir(search_cli)
        printInfo(ctx.get_help())
        return

    if buildindex:
        set_up_env() # rebuild static files
        build_website()
        return


    if runserver:
        run_server.go(port)
        return

    if keyword:
        query_file = gen_sql_from_keyword(keyword)
        filename = [query_file]


    if filename:

        # Check if we have a folder, or process a single sql file
        files = []
        if os.path.isdir(filename[0]):
            dir = filename[0]
            for f in os.listdir(dir):
                if f.endswith(".sql"):
                    files.append(os.path.join(dir, f))
        else:
            if os.path.isfile(filename[0]) and filename[0].endswith(".sql"):
                files.append(filename[0])
        if not files:
            printDebug("No files found.", "red")
            return


        set_up_env()
        user_login() # GBQ connection setup


        # Build the networks for each file (default: overwrite pre-existing)
        for sql_file in files:
            printInfo("Reading file: {}".format(sql_file))
            metadata = extract_query_metadata(sql_file, verbose=True)
            
            if fulldimensions:
                printInfo("..using full Dimensions data", "red")
            
            for task in metadata["network_types"]:

                if task == 'organizations':
                    db_data = gen_orgs_collab_network(sql_file, metadata, fulldimensions, verbose)
                    render_json(
                        db_data,
                        task,
                        'Organization', 
                        'Organization',
                        sql_file
                    )

                elif task == 'concepts':
                    db_data = gen_concept_network(sql_file, metadata, fulldimensions, verbose)
                    render_json(
                        db_data,
                        task,
                        'Concept', 
                        'Concept',
                        sql_file, 
                    )
                else:
                    printDebug("Failed to start network generation of type: {}".format(task), "red")
                    printDebug("   ... your query configuration does not match the valid network types: {}".format(NETWORK_TYPES), "comment")

        # rebuild the website
        build_website()



if __name__ == '__main__':
    main_cli()
