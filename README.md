# Dimensions Network Generation tool

A Python tool for creating network visualizations powered by data from Dimensions on Google BigQuery. 

Currenlty the main output visualization supported is VOSviewer. More visualizations will be added in the future.

## Datasets

By default the tool uses the [Dimensions COVID-19 dataset](https://console.cloud.google.com/marketplace/product/digitalscience-public/covid-19-dataset-dimensions) that is openly available on the Google Cloud Marketplace, and contains all published articles and preprints, grants, clinical trials, and research datasets from Dimensions.ai that are related to COVID-19.

At time of writing (May 2022), the dataset contains:

* 1M+  Publications and preprints
* 16k+ Grants
* 41k+ Patents
* 14k+ Clinical Trials
* 32k+ Research Datasets
* 36k+ Research Organizations


### How to use the full Dimensions dataset

The tool can be updated to so use the full Dimensions dataset (subscription-based). See the relevant `USE_COVID_DIMENSIONS` setting in `settings.py`. 

## Example outputs

![concepts-network](/screenshots/concepts-network.png)

![organizations-network.png](/screenshots/organizations-network.png)



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


## Installation

> REVIEW

```sh
git clone git@github.com:digital-science/dimensions-network-gen.git
cd dimensions-network-gen
python3 -m venv .
source bin/activate
pip3 install -r requirements.txt
pip install -e .
dim-networkgen --help
```

## Running

After installation, you can run the application by calling `dim-networkgen`.

```
$ dim-networkgen
Usage: dim-networkgen [OPTIONS] [FILENAME]...

  dim-networkgen: a tool for creating network visualizations powered by data
  from Dimensions on Google BigQuery.

  FILENAME. The name of the file in the 'input' directory to be converted into
  a network.

Options:
  -a, --buildall      Call BigQuery and construct network definitions.
  -o, --overwrite     By default, existing networks are not recalculated when
                      the 'buildall' script is run. The overwrite flag
                      indicates all input files should be reevaluated,
                      regardless of whether an output file already exists.
  -s, --server        Start the webserver.
  -p, --port INTEGER  Specify the port on which the webserver should listen
                      for connections (default: 8009).
  --examples          Show some examples
  --verbose           Verbose mode
  --help              Show this message and exit.
```


### Command-line options

> REVIEW

The command accepts several optional flags. The main actions are `buildall`, `build` and `server`. **If none of these three flags are supplied, the default approach is to complete the `buildall` and `server` steps.**:

* `-a`, `--buildall`: Run the steps that call BigQuery, build the network files, and prepare the website. Will retrieve and process all files from the `input` directory.
* `-b`, `--build $INPUT_FILE`: The same steps as `buildall`, except the user can specify a single input file to be processed, instead of processing all of them.
* `-s`, `--server`: Start the web server (on `localhost:8000`) that displays the web site generated in the "build" step.
* `-o`, `--overwrite`: Modifies the `buildall` operation. By default, existing networks are not recalculated when the `buildall` script is run. The overwrite flag indicates all input files should be reevaluated, regardless of whether an output file already exists.
* `-p`, `--port $PORT_NUM`: Modifies the `server` operation. Specifies the port on which the web server is listening. Default is 8000.

