#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import click

from .settings import *
from .networkgen.helpers import *
from .networkgen import network 
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
    "--server", "-s",
    is_flag=True,
    help="Start the webserver.")
@click.option(
    "--port", "-p", default=8009,
    help="Specify the port on which the webserver should listen for connections (default: 8009).")
@click.option('--verbose', is_flag=True, help='Verbose mode')
@click.pass_context
def main_cli(ctx, filename=None,  
                verbose=False, 
                buildindex=False, 
                fulldimensions=False, 
                server=False, 
                port=None,):
    """dimensions-network: a tool for creating network visualizations powered by data from Dimensions on Google BigQuery. Example: 

dimensions-network {QUERY_FILE}

QUERY_FILE. File name containing the GBQ query to be converted into a network. If a folder is passed, all files in the folder will be processed.     
"""

    if not filename and not server and not buildindex:
        # print dir(search_cli)
        printInfo(ctx.get_help())
        return

    if filename:

        files = []
        if os.path.isdir(filename[0]):
            dir = filename[0]
            for f in os.listdir(dir):
                if f.endswith(".sql"):
                    files.append(os.path.join(dir, f))
        else:
            if os.path.isfile(filename[0]) and filename[0].endswith(".sql"):
                files.append(filename[0])
        
        if files:
            for f in files:
                printInfo("Found file: {}".format(f), "comment")
        else:
            printDebug("No files found.", "red")
            return


        # GBQ connection setup
        set_up_env()
        user_login()


        # Build the networks for each file (default: overwrite existing files)
        for f in files:
            printInfo("Processing file: {}".format(f), "comment")
            metadata = extract_query_metadata(f)
            printInfo("Metadata: {}".format(metadata), "comment")
            
            for task in metadata["network_types"]:
                if task == 'collab_orgs':
                    network.gen_orgs_collab_network(f, metadata, fulldimensions, verbose)
                elif task == 'concepts':
                    network.gen_concept_network(f, metadata, fulldimensions, verbose)
                else:
                    printDebug("Failed to start network generation of type: {}".format(task), "red")
                    printDebug("   ... your query configuration does not match the valid network types: {}".format(NETWORK_TYPES), "comment")

        # always rebuild the index when network data is generated
        buildindex = True



    if buildindex:
        network.gen_index()
        printInfo("Index page regenerated.", "comment")


    if server:
        run_server.go(port)




if __name__ == '__main__':
    main_cli()
