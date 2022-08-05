#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Helper functions for networkgen library
"""

from collections import defaultdict
import configparser
import os
import subprocess
from shutil import copytree, ignore_patterns
import click

from ..settings import *
from . import bqdata



#
#
# GOOGLE & GBQ UTILITIES
#
#


def _test_user_login():
    """
    Returns a boolean value indicating whether the user
    is currently authenticated to the Google Cloud Platform
    API.
    """
    try:
        db = bqdata.Client()
    except OSError as x:
        return False
    return True



def user_login():
    """
    Handles the process of logging a user into GCP via
    the gcloud command-line tool. Does not return anything,
    but does exit if the `gcloud` command cannot be found
    on the local machine.
    """

    # If they're already logged in, we're good:
    if _test_user_login():
        printDebug('Gcloud credentials found. Skipping login.', "comment")
        return

    printDebug('Gcloud: Logging in..', "comment")
    # if they aren't logged in, do it:
    bashCommand = "gcloud auth login --brief"
    try:
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    except FileNotFoundError:
        printDebug("""
        ERROR: Attempted to run `gcloud auth login` to obtain
        Google Cloud credentials, but the command could not be found.
        Please install gcloud: https://cloud.google.com/sdk/gcloud
        """)
        exit(1)
    output, error = process.communicate()


def gbq_dataset_name(fulldimensions_flag):
    """
    Returns the name of the dataset in Google BigQuery.
    """
    if not fulldimensions_flag:
        return "covid-19-dimensions-ai.data"
    else:
        return "dimensions-ai.data_analytics"





#
#
# FILES & SQL PARSING UTILITIES
#
#



def set_up_env():
    "Set up basic environment"
    

    # make sure output directories are there
    for task in NETWORK_TYPES:
        try:
            os.makedirs(f'{DEFAULT_OUTPUT_JSON_PATH}/{task}')
        except FileExistsError:
            pass

    # copy all static files
    copytree(PROJECT_STATIC_PATH, DEFAULT_OUTPUT_PATH, dirs_exist_ok=True, ignore=ignore_patterns('index_template.html',))

    return



def extract_query_metadata(sql_file):
    """
    Extracts metadata from a SQL file. 
    
    Return values found or defaults if not found.
    If a value provided is not accepted, raise an exception.

    """

    with open(sql_file, "r") as input:
        data = input.readlines()

    METADATA = dict(NETWORK_PARAMETERS_DEFAULT)

    for p in NETWORK_PARAMETERS_DEFAULT:
        for l in data:
            if l.startswith("--"):
                l = l.strip("--").strip()
                if p+":" in l:
                    l = l.split(":")
                    METADATA[p] = l[1].strip()

    # turn the comma separated string into a list we can iterate over
    METADATA["network_types"] = METADATA["network_types"].replace(",", " ").split()
    return METADATA






#
#
# INDEX CREATION UTILITIES
#
#



def list_networks(tasks, root=DEFAULT_OUTPUT_JSON_PATH):
    """
    Returns the filenames of all files (and directories)
    ending with a ".json" extension in the web/networks directory.

    Inputs:
        - tasks (list): Each type of network the script generates.
            Corresponds to the names of the directories within 'root'
        - root (string): Each task has a separate output directory.
            This is the path to the directory that holds those
            directories. Ex: "web/networks"

    Returns:
        A dict with format {'sql-topic-name': ['collab_orgs', 'concepts']}
    """

    results = defaultdict(list)
    for task in tasks:
        # HACK: we should make sure all files are there for both types
        output_names = os.listdir(f'{root}/{task}')
        filtered = [x[:-5] for x in output_names if x[-5:] == '.json']

        for topic in filtered:
            results[topic].append(task)

    return results




def gen_index():
    """
    Generates the dynamic component of the web page that
    displays links to all the generated networks. Combines
    input data with "index_template.html" to generate
    a file called "index.html".
    """

    todo = list_networks(NETWORK_TYPES)

    if len(todo.keys()) > 0:
        body = ""
        for topic, network_types in todo.items():
            body += """<div class="col-md-4"><div class="card"> """
            topic_nice = topic.replace("_", " ").replace("-", " ").capitalize()
            body += f"<h6 class='card-header'>Query: {topic_nice}</h6>"
            body += """<div class="card-body">Visualizations:"""

            for network_type in network_types:
            
                _url = f"vosviewer.html?json=json/{network_type}/{topic}.json&max_label_length=60&max_n_links=500&repulsion=2"
                body += f"""<li><a href='{_url}' target='_blank'>{network_type}</a></li>"""

            body += """</div></div></div>"""

        body += "<hr>"
    else:
        body = "<em>(No network definitions were found.)</em>"

    with open(f'{PROJECT_STATIC_PATH}/index_template.html', "r") as input:
        template = input.read()
    template = template.replace('<!-- BODY HERE -->', body)

    with open(f'{DEFAULT_OUTPUT_PATH}/index.html', "w") as output:
        output.write(template)







#
#
# Generic Python utils 
#
#



def printDebug(text, mystyle="", err=True, **kwargs):
    """Wrapper around click.secho() for printing in colors with various defaults.

    :kwargs = you can do printDebug("s", bold=True)

    2018-12-06: by default print to standard error stderr (err=True)
    https://click.palletsprojects.com/en/5.x/api/#click.echo
    This means that the output is ok with `less` and when piped to other commands (or files)

    Styling output:
    <http://click.pocoo.org/5/api/#click.style>
    Styles a text with ANSI styles and returns the new string. By default the styling is self contained which means that at the end of the string a reset code is issued. This can be prevented by passing reset=False.

    This works also with inner click styles eg

    ```python
    uri, title = "http://example.com", "My ontology"
    printDebug(click.style("[%d]" % 1, fg='blue') +
               click.style(uri + " ==> ", fg='black') +
               click.style(title, fg='red'))
    ```

    Or even with Colorama

    ```
    from colorama import Fore, Style

    printDebug(Fore.BLUE + Style.BRIGHT + "[%d]" % 1 + 
            Style.RESET_ALL + uri + " ==> " + Fore.RED + title + 
            Style.RESET_ALL)
    ```


    Examples:

    click.echo(click.style('Hello World!', fg='green'))
    click.echo(click.style('ATTENTION!', blink=True))
    click.echo(click.style('Some things', reverse=True, fg='cyan'))
    Supported color names:

    black (might be a gray)
    red
    green
    yellow (might be an orange)
    blue
    magenta
    cyan
    white (might be light gray)
    reset (reset the color code only)
    New in version 2.0.

    Parameters:
    text – the string to style with ansi codes.
    fg – if provided this will become the foreground color.
    bg – if provided this will become the background color.
    bold – if provided this will enable or disable bold mode.
    dim – if provided this will enable or disable dim mode. This is badly supported.
    underline – if provided this will enable or disable underline.
    blink – if provided this will enable or disable blinking.
    reverse – if provided this will enable or disable inverse rendering (foreground becomes background and the other way round).
    reset – by default a reset-all code is added at the end of the string which means that styles do not carry over. This can be disabled to compose styles.

    """

    if mystyle == "comment":
        click.secho(text, dim=True, err=err)
    elif mystyle == "important":
        click.secho(text, bold=True, err=err)
    elif mystyle == "normal":
        click.secho(text, reset=True, err=err)
    elif mystyle == "red" or mystyle == "error":
        click.secho(text, fg='red', err=err)
    elif mystyle == "green":
        click.secho(text, fg='green', err=err)
    else:
        click.secho(text, err=err, **kwargs)




def printInfo(text, mystyle="", **kwargs):
    """Wrapper around printDebug for printing ALWAYS to stdout
    This means that the output can be grepped, or used with unix pipes etc.. 
    """
    printDebug(text, mystyle, False, **kwargs)
