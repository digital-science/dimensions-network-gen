#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Helper functions for networkgen library
"""

from collections import defaultdict
import configparser
import os
import subprocess
import shutil
import click

from ..settings import *
from . import bqdata



def set_up_env():
    "Set up basic environment"
    

    # make sure input directory is there
    try:
        os.makedirs(DEFAULT_INPUT_LOCATION)
    except FileExistsError:
        pass

    # make sure output directories are there
    for task in TASKS:
        try:
            os.makedirs(f'{DEFAULT_OUTPUT_NETWORKS}/{task}')
        except FileExistsError:
            pass

    # copy all static files
    shutil.copytree(PROJECT_STATIC_FOLDER, DEFAULT_OUTPUT_LOCATION, dirs_exist_ok=True)


    # read configuration
    config = configparser.ConfigParser()
    config.read(DEFAULT_NETWORK_INIT)

    # printDebug(f'DEBUG: config file: {config.sections()}')

    # defines how to parse each config value
    # we need
    convert = {
        'collab_authors': {
            'max_nodes': int,
            'min_edge_weight': int
        },
        'collab_orgs': {
            'max_nodes': int,
            'min_edge_weight': int
        },
        'concepts': {
            'max_nodes': int,
            'min_link_relevance': float,
            'min_concept_frequency': int,
            'min_edge_weight': int
        }
    }
    parsed = {}
    for section, fields in convert.items():
        parsed[section] = {}
        for field in fields:
            # printDebug(f'DEBUG: Parsing {section} {field}')
            func = convert[section][field]
            parsed[section][field] = func(config[section][field])
    return parsed




def list_networks(tasks, root=DEFAULT_OUTPUT_NETWORKS):
    """
    Returns the filenames of all files (and directories)
    ending with a ".json" extension in the web/networks directory.

    Inputs:
        - tasks (list): Each type of network the script generates.
            Corresponds to the names of the directories within 'root'
        - root (string): Each task has a separate output directory.
            This is the path to the directory that holds those
            directories. Ex: "web/networks"
    """

    results = defaultdict(list)
    for task in tasks:
        # HACK: we should make sure all files are there for both types
        output_names = os.listdir(f'{root}/{task}')
        filtered = [x[:-5] for x in output_names if x[-5:] == '.json']

        for topic in filtered:
            results[topic].append(task)

    return results




def determine_todo(dirname=DEFAULT_INPUT_LOCATION, overwrite=False, single_topic=None):
    """
    Returns the filenames of all files (and directories)
    ending with a ".sql" extension in the specified directory.
    It does NOT return results that already have results generated.

    Inputs:
      - dirname (string): path to the directory of interest.
            Accepts absolute or relative paths.
      - overwrite (bool): When True, existing JSON files will
            be discarded in favor of newly calculated ones. When
            False, input SQL files with existing output JSON
            files will be skipped.
    """

    todo = defaultdict(list)

    if single_topic is not None:
        inputs = [single_topic]
    else:
        input_names = os.listdir(dirname)
        inputs = [x[:-4] for x in input_names if x[-4:] == '.sql']

    done = list_networks(TASKS)

    for input in inputs:
        for task in TASKS:
            if overwrite or task not in done[input]:
                todo[input].append(task)

    return todo




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
        printDebug('DEBUG: gcloud credentials found. Skipping login.')
        return

    printDebug('DEBUG: Logging in.')
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




# """
# Generic Python utils 
# """

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
