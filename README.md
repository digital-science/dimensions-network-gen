# Dimensions Network Generation tool

A tool for creating network visualizations powered by data from Dimensions on G
Google BigQuery. Currenlty the main output visualization is VOSviewer. More visualizations will be added in the future.

## Installation

If you are only viewing already-created networks, no external software is required. However, **connecting to BigQuery to generate new networks requires the installation of the Google Cloud SDK**, "gcloud," available [directly from Google](https://cloud.google.com/sdk/docs/install). If you can open a terminal and the `gcloud` command is recognized, it has been sufficiently configured.

## Input

* Network-level configuration options are defined in the file at `user-input/config.ini`.
* Each visualization generated is based on a subset of publications that you can define using SQL. **These definitions are stored in the `user-input/` directory**.
* Each file should contain a single SQL query that returns a list of Dimensions publication IDs **in a field called `id`**.
* File names should be of the format `$title.sql`.
  * For example, a file called `archaeology.sql` will create a network listed under the title "archaeology".

Example contents of `archaeology.sql`:

> UPDATE

```sql
SELECT id
FROM `covid-19-dimensions-ai.data.publications`
WHERE
    year >= 2019
    AND '2101' IN UNNEST(category_for.second_level.codes)
```

## Running

> UPDATE

```sh
git clone git@gitlab.com:digital-science/dimensions/data-solutions/networkgen.git
cd networkgen
python3 -m venv .
source bin/activate
pip3 install -r requirements.txt
cd networkgen # yes, this happens twice

# if you want to run tests:
python3 -m unittest
# if you want to just execute the script:
python3 networkgen.py
```

### Command-line options

> UPDATE

The `python3 networkgen.py` command accepts several optional flags. The main actions are `buildall`, `build` and `server`. **If none of these three flags are supplied, the default approach is to complete the `buildall` and `server` steps.**:

* `-a`, `--buildall`: Run the steps that call BigQuery, build the network files, and prepare the website. Will retrieve and process all files from the `input` directory.
* `-b`, `--build $INPUT_FILE`: The same steps as `buildall`, except the user can specify a single input file to be processed, instead of processing all of them.
* `-s`, `--server`: Start the web server (on `localhost:8000`) that displays the web site generated in the "build" step.

#### Options

> UPDATE

* `-o`, `--overwrite`: Modifies the `buildall` operation. By default, existing networks are not recalculated when the `buildall` script is run. The overwrite flag indicates all input files should be reevaluated, regardless of whether an output file already exists.
* `-p`, `--port $PORT_NUM`: Modifies the `server` operation. Specifies the port on which the web server is listening. Default is 8000.

Examples:

```sh
# Fetch data using the files in the
# input/ directory, generate networks,
# and launch a web server:
python3 networkgen.py

# Just build new networks and exit:
python3 networkgen.py --buildall
```

