# Dimensions Network Generation tool

A Python tool for creating network visualizations powered by data from Dimensions on Google BigQuery. 


## Visualization

Currenlty the main output visualization supported is [VOSviewer](https://www.vosviewer.com/). More visualizations will be added in the future.

### Example outputs

A concept network:
![concepts-network](/screenshots/concepts-network.png)

An organization collaboration network:

![organizations-network.png](/screenshots/organizations-network.png)



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

The tool can be updated to so use the full Dimensions dataset (subscription-based). 

Pass the `-d` option when invoking the script. 


## Installation

If you are only viewing already-created networks, no external software is required. However, **connecting to BigQuery to generate new networks requires the installation of the Google Cloud SDK**, "gcloud," available [directly from Google](https://cloud.google.com/sdk/docs/install). If you can open a terminal and the `gcloud` command is recognized, it has been sufficiently configured.

## Input

* Network-level configuration options are defined in the file at `user-input/config.ini`.
* Each visualization generated is based on a subset of publications that you can define using SQL. **Example SQL definitions are stored in the `user-input-examples/` directory**.
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



With Python 3.9 and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/index.html)

```bash
$ git clone git@github.com:digital-science/dimensions-network-gen.git
$ mkvirtualenv dim-network-gen
$ pip install -r requirements.txt
$ pip install -e .
```


## Running

After installation, you can run the application by calling `dim-networkgen`.

```bash
$ dim-networkgen
Usage: dim-networkgen [OPTIONS] [FILENAME]...

  dim-networkgen: a tool for creating network visualizations powered by data
  from Dimensions on Google BigQuery. Example:

  networkgen {QUERY_FILE}

  QUERY_FILE. File name containing the GBQ query to be converted into a
  network. If a folder is passed, all files in the folder will be processed.

Options:
  -i, --buildindex      Just build the index page listing out previously
                        created networks.
  -f, --fulldimensions  Query using the full Dimensions dataset, instead of
                        the COVID19 subset (note: requires subscription).
  -s, --server          Start the webserver.
  -p, --port INTEGER    Specify the port on which the webserver should listen
                        for connections (default: 8009).
  --verbose             Verbose mode
  --help                Show this message and exit.
```

