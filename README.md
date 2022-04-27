# Dimensions Network Generation tool

A tool for creating network visualizations powered by data from Dimensions on Google BigQuery. 

Currenlty the main output visualization is VOSviewer. More visualizations will be added in the future.

## Datasets

By default the tool uses the [Dimensions COVID-19 dataset](https://console.cloud.google.com/marketplace/product/digitalscience-public/covid-19-dataset-dimensions) that is openly available on the Google Cloud Marketplace, and contains all published articles and preprints, grants, clinical trials, and research datasets from Dimensions.ai that are related to COVID-19.

At time of writing (Feb 2021), the dataset contains:

* 300k+ publications and preprints
* 5000+ grants worth £4.5bn+
* 8000+ clinical trials
* 10k+ research datasets
* 100k+ research organizations

### How to use the full Dimensions dataset

The tool can be updated to so use the full Dimensions dataset (subscription-based). See the relevant `USE_COVID_DIMENSIONS` setting in `settings.py`. 


## Installation

If you are only viewing already-created networks, no external software is required. However, **connecting to BigQuery to generate new networks requires the installation of the Google Cloud SDK**, "gcloud," available [directly from Google](https://cloud.google.com/sdk/docs/install). If you can open a terminal and the `gcloud` command is recognized, it has been sufficiently configured.

## Input

* Network-level configuration options are defined in the file at `user-input/config.ini`.
* Each visualization generated is based on a subset of publications that you can define using SQL. **These definitions are stored in the `user-input/` directory**.
* Each file should contain a single SQL query that returns a list of Dimensions publication IDs **in a field called `id`**.
* File names should be of the format `$title.sql`.
  * For example, a file called `archaeology.sql` will create a network listed under the title "archaeology".

Example contents of `last_30_days.sql`:

```sql
select id
from `covid-19-dimensions-ai.data.publications`
where 
EXTRACT(DATE FROM date_inserted) >= DATE_ADD(CURRENT_DATE(), INTERVAL -30 DAY)
```

## Running

> UPDATE

```sh
git clone git@github.com:digital-science/dimensions-network-gen.git
cd dimensions-network-gen
python3 -m venv .
source bin/activate
pip3 install -r requirements.txt
pip install -e .
dim-networkgen --help
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

