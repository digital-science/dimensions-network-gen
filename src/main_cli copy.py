#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import click

from .networkgen.helpers import *
from .networkgen import network 
from .networkgen import server as run_server 



@click.command()
@click.argument('filename', nargs=-1)
@click.option(
    "--buildall", "-a",
    is_flag=True,
    help="Call BigQuery and construct network definitions.")
@click.option(
    "--overwrite", "-o",
    is_flag=True,
    help="By default, existing networks are not recalculated when the 'buildall' script is run. The overwrite flag indicates all input files should be reevaluated, regardless of whether an output file already exists.")
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
                buildall=False, 
                overwrite=False, 
                fulldimensions=False, 
                server=False, 
                port=None,):
    """dim-networkgen: a tool for creating network visualizations powered by data from Dimensions on Google BigQuery. Example: 

networkgen {QUERY_FILE}

QUERY_FILE. File name containing the GBQ query to be converted into a network. If a folder is passed, all files in the folder will be processed.     
"""

    if not filename and not server:
        # print dir(search_cli)
        printInfo(ctx.get_help())
        return

    # print(filename)
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


    # build the networks 

    for f in files:

        

    single_topic = None
    if filename:
        single_topic = filename[0]
        if "/" in single_topic:
            single_topic = single_topic.split("/")[1]
        single_topic = single_topic.replace(".sql", "")

    # start script

    config = set_up_env()

    if single_topic:
        todo = determine_todo(overwrite=overwrite, single_topic=single_topic)

        if len(todo.keys()) > 0:
            # We only need a GCP login if the user's building a
            # new network.
            user_login()

            for topic, tasks in todo.items():
                for task in tasks:
                    if task == 'collab_orgs':
                        network.gen_orgs_collab_network(topic, config['collab_orgs'], verbose)
                    elif task == 'concepts':
                        network.gen_concept_network(topic, config['concepts'], verbose)
        else:
            printDebug('There were no input files detected in the "input" directory that did not already have networks defined. To recalculate these networks, include the `--overwrite` flag.\n')

    # Regardless of whether the server is being launched, we
    # want to rebuild the index page, in case network files
    # and/or input files have been removed.
    network.gen_index()

    if server:
        run_server.go(port)




if __name__ == '__main__':
    main_cli()
