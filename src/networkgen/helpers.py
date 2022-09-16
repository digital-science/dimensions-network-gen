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







def set_up_env(verbose=True):
    """Set up basic environment
    
    a) ensure all folders for local topics/json and for the website output are there, so that later we can write into them
    b) clean up topics json folder ie ensure that all json network files have a corresponding SQL topic defintion - otherwise remove it.
    """
    printInfo(f"Setting up application directories ...")

    if not os.path.exists(DEFAULT_TOPICS_JSON_PATH):
        os.makedirs(DEFAULT_TOPICS_JSON_PATH)

    for task in NETWORK_TYPES:
        try:
            os.makedirs(f'{DEFAULT_TOPICS_JSON_PATH}/{task}')
        except FileExistsError:
            pass

    printInfo(f"Cleaning up unused JSON files... ", "comment")
    # REMOVE STRAY JSON FILES IF THEY DON'T HAVE A SQL TOPIC
    for task in NETWORK_TYPES:
        json_files = os.listdir(f'{DEFAULT_TOPICS_JSON_PATH}/{task}')
        for f in json_files:
            f_sql = f.replace(".json", ".sql")
            if not os.path.exists(f"{DEFAULT_TOPICS_SQL_PATH}/{f_sql}"):
                os.remove(f'{DEFAULT_TOPICS_JSON_PATH}/{task}/{f}')
                printInfo(f"\t..deleted {DEFAULT_TOPICS_JSON_PATH}/{task}/{f}", "comment")   

    return





def get_valid_topics():
    """List the topics that have both SQL and JSON files
    """
    topics = []
    for task in NETWORK_TYPES:
        json_files = os.listdir(f'{DEFAULT_TOPICS_JSON_PATH}/{task}')
        for f in json_files:
            if f.endswith(".json"):
                f_sql = f.replace(".json", ".sql")
                if os.path.exists(f"{DEFAULT_TOPICS_SQL_PATH}/{f_sql}"):
                    topics += [f_sql] 

    return list(set(topics))




def build_website():
    """
    Generates the website listing out all available science maps.
    Combines input data with "index_template.html" to generate
    a file called "index.html".

    """
    printInfo("Generating website pages..")

    # copy all HTML static files
    copytree(PROJECT_STATIC_PATH, DEFAULT_BUILD_PATH, dirs_exist_ok=True, ignore=ignore_patterns('index_template.html',))

    # copy all TOPICS SQL and JSON
    copytree(DEFAULT_TOPICS_SQL_PATH, DEFAULT_BUILD_TOPICS_PATH, dirs_exist_ok=True)

    # valid topics are sql files that have a json dataset as well
    valid_topics = [x.replace(".sql", "") for x in get_valid_topics()]
    DEFAULT_NETWORK_TYPE = NETWORK_TYPES[0]

    def get_sqlquery_contents(topic):
        try:
            with open(f"{DEFAULT_BUILD_TOPICS_PATH}/{topic}.sql", "r") as input:
                return input.read()
        except:
            printInfo(f"  => SQL query for topic '{topic}' not found in {DEFAULT_BUILD_TOPICS_PATH}")
            return "No SQL found"

    if len(valid_topics) > 0:
        body = ""
        for topic in sorted(valid_topics):
            body += """<div class="col-md-6"><div class="card"> """
            topic_nice = topic.replace("_", " ").replace("-", " ").capitalize()
            # body += f"<h6 class='card-header'>Topic: <span style='color: darkred'>{topic_nice}</span></h6>"
            
            _url = f"wrapper.html?topicId={topic}&network={DEFAULT_NETWORK_TYPE}"
            body += f"<h6 class='card-header'>Topic: <a href='{_url}' target='_blank'>{topic_nice}</a></h6>"
            body += """<div class="card-body"><small>Query:</small> <br /><br />"""

            sql = get_sqlquery_contents(topic)
            body += f"""<pre>{sql}</pre></div></div></div>"""

        body += ""

    else:
        body = "<em>(No network definitions were found.)</em>"

    with open(f'{PROJECT_STATIC_PATH}/index_template.html', "r") as input:
        template = input.read()
    template = template.replace('<!-- BODY HERE -->', body)

    outpath = f'{DEFAULT_BUILD_PATH}/index.html'
    with open(outpath, "w") as output:
        output.write(template)

    printInfo(f"  Saved: {outpath}", "comment")








def extract_query_metadata(sql_file, verbose=False):
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

    if verbose:
        printInfo("Network parameters:", "comment")
        for k,v in METADATA.items():
            printInfo(f"  -{k}: {v}", "comment")
    return METADATA



from string import Template
from datetime import date

def gen_sql_from_keyword(keyword, verbose=True):
    """Save a SQL query from a keyword
    TODO
    - handle spaces and quotes
    - handle multi words
    
    """

    q = Template("""
-- AUTOMATICALLY GENERATED KEYWORD SEARCH QUERY
-- date: $date
-- max_nodes: 400 
-- min_edge_weight: 1
-- min_concept_relevance: 0.5
-- min_concept_frequency: 2

select id
from `covid-19-dimensions-ai.data.publications`
where 
REGEXP_CONTAINS(abstract.preferred, r'$key')
OR
REGEXP_CONTAINS(title.preferred, r'$key')
    """)

    today = date.today()
    st = today.strftime("%b-%d-%Y")

    data = q.substitute(key=keyword, date=st)
    filename = "".join([c for c in keyword if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
    filepath = f"{DEFAULT_TOPICS_SQL_PATH}/{filename}.sql"

    with open(filepath, "w") as f:
        f.write(data)

    if verbose:
        printInfo(f"  Saved: {filepath}", "comment")

    return filepath









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
