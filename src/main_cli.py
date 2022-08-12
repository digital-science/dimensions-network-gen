#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import click

from .settings import *
from .networkgen.helpers import *
from .networkgen import networkgen 
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
                runserver=False, 
                port=None,):
    """dim-networkgen: a tool for creating network visualizations powered by data from Dimensions on Google BigQuery. Example: 

dim-networkgen {QUERY_FILE}

QUERY_FILE. File name containing the GBQ query to be converted into a network. If a folder is passed, all files in the folder will be processed.     
"""

    if not filename and not runserver and not buildindex:
        # print dir(search_cli)
        printInfo(ctx.get_help())
        return

    elif buildindex:
        set_up_env() # rebuild static files
        gen_index()


    elif runserver:
        run_server.go(port)


    elif filename:

        # Ensure that files exist and list them
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


        # GBQ connection setup
        set_up_env()
        user_login()


        # Build the networks for each file (default: overwrite existing files)
        for f in files:
            printInfo("Reading file: {}".format(f))
            metadata = extract_query_metadata(f, verbose=True)
            
            if fulldimensions:
                printInfo("..using full Dimensions data", "red")
            
            for task in metadata["network_types"]:
                if task == 'organizations':
                    networkgen.gen_orgs_collab_network(f, metadata, fulldimensions, verbose)
                elif task == 'concepts':
                    networkgen.gen_concept_network(f, metadata, fulldimensions, verbose)
                else:
                    printDebug("Failed to start network generation of type: {}".format(task), "red")
                    printDebug("   ... your query configuration does not match the valid network types: {}".format(NETWORK_TYPES), "comment")

        # rebuild the index page
        gen_index()

        if click.confirm("Start the server?"):
            run_server.go(port)





if __name__ == '__main__':
    main_cli()
