#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import click

from .networkgen.helpers import *
from .networkgen import network 
from .networkgen import server as run_server 


CMD_LINE_EXAMPLES = """SOME EXAMPLES HERE:
$ networkgen
 => returns some nice text
"""



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
    "--server", "-s",
    is_flag=True,
    help="Start the webserver.")
@click.option(
    "--port", "-p", default=8009,
    help="Specify the port on which the webserver should listen for connections (default: 8000).")
@click.option('--examples', is_flag=True, help='Show some examples')
@click.pass_context
def main_cli(ctx, filename=None,  
                examples=False, 
                buildall=False, 
                overwrite=False, 
                server=False, 
                port=None,):
    """networkgen: a tool for creating VOSviewer network visualizations powered by data from Dimensions on G
Google BigQuery.

FILENAME. The name of the file in the 'input' directory to be converted into a network.     
"""

    if examples:
        printInfo(CMD_LINE_EXAMPLES, fg="green")
        return

    if not filename and not buildall and not server:
        # print dir(search_cli)
        printInfo(ctx.get_help())
        return

    single_topic = None
    if filename:
        single_topic = filename[0]
        if "/" in single_topic:
            single_topic = single_topic.split("/")[1]
        single_topic = single_topic.replace(".sql", "")

    # start script

    config = set_up_env()

    if single_topic or buildall:
        todo = determine_todo(overwrite=overwrite, single_topic=single_topic)

        if len(todo.keys()) > 0:
            # We only need a GCP login if the user's building a
            # new network.
            user_login()

            for topic, tasks in todo.items():
                for task in tasks:
                    if task == 'collab_authors':
                        network.gen_collab_network(topic, config['collab_authors'])
                    elif task == 'collab_orgs':
                        network.gen_orgs_collab_network(topic, config['collab_orgs'], verbose=True)
                    elif task == 'concepts':
                        network.gen_concept_network(topic, config['concepts'])
        else:
            printDebug('There were no input files detected in the "input" directory that did not already have networks defined. To recalculate these networks, include the `--overwrite` flag.\n')

    # Regardless of whether the server is being launched, we
    # want to rebuild the index page, in case network files
    # and/or input files have been removed.
    network.gen_index()

    if server or buildall:
        run_server.go(port)




if __name__ == '__main__':
    main_cli()
