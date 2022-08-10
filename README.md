# Dimensions Network Generation tool

A Python tool that streamlines the process of creating [scientific networks visualizations](https://digital-science.github.io/dimensions-network-gen/index.html), by using data from [Dimensions on Google BigQuery](https://www.dimensions.ai/products/bigquery/). 

Currenlty the only output visualization supported is [VOSviewer](https://www.vosviewer.com/). More visualizations will be added in the future.

Examples:

* https://digital-science.github.io/dimensions-network-gen/index.html


## Datasets

By default the tool uses the [Dimensions COVID-19 dataset](https://console.cloud.google.com/marketplace/product/digitalscience-public/covid-19-dataset-dimensions). The dataset is openly available on the Google Cloud Marketplace and contains all published articles and preprints, grants, clinical trials, and research datasets from Dimensions.ai that are related to COVID-19.

At time of writing (May 2022), the dataset contains:

* 1M+  Publications and preprints
* 16k+ Grants
* 41k+ Patents
* 14k+ Clinical Trials
* 32k+ Research Datasets
* 36k+ Research Organizations

Data model: see the [official documentation](https://docs.dimensions.ai/bigquery/data-sources.html).

### Using the full Dimensions dataset

Users with an active subscription to the full [Dimensions on Google BigQuery](https://www.dimensions.ai/products/bigquery) dataset can perform network analyses using all data in Dimensions, not just the COVID19 subset.  

In order to do so, pass the `--fulldimensions` (or `-f`) option when invoking the script. E.g.

```
$ dimensions-network {SQL_QUERY_FILE} --fulldimensions
```

### Accessing BigQuery 

In order to access the Dimensions datasets, you need to be able to connect to [Google BigQuery](https://cloud.google.com/bigquery/) using Python. This means:

* **Installing the SDK**. Installing & authorizing the the Google Cloud SDK, "gcloud," available [directly from Google](https://cloud.google.com/sdk/docs/install). If you can open a terminal and the `gcloud` command is recognized, it has been sufficiently configured.
* **Setting up a GCP project**. Each time you interact with BigQuery, you need to specify which GCP project you are using. This is generally used for resources access management. More info [here](https://docs.dimensions.ai/bigquery/gcp-setup.html).

Note: newly created projects which have no associated billing account provide a [sandbox](https://cloud.google.com/bigquery/docs/sandbox) experience, providing initial access to the [free tier](https://cloud.google.com/free) of BigQuery provided by Google. The free tier is more than enough for using this library.  



## Installation

With Python 3.9 and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/index.html)

```bash
$ git clone git@github.com:digital-science/dimensions-network-gen.git
$ mkvirtualenv dimensions-network
$ pip install -r requirements.txt
$ pip install -e .
```


## Running

After installation, you can run the application by calling `dimensions-network`.

```bash
$ dimensions-network
Usage: dimensions-network [OPTIONS] [FILENAME]...

  dimensions-network: a tool for creating network visualizations powered by data
  from Dimensions on Google BigQuery. Example:

  dimensions-network {QUERY_FILE}

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

## Input files

Visualizations are generated based on a subset of publications that you can define using SQL.

* Each visualization is triggered by a corresponding SQL file containing a query and, optionally, some configuration directives. 
* Example SQL definitions are stored in the `user-input-examples/` directory.
* Each file should contain a single SQL query that returns a list of Dimensions publication IDs **in a field called `id`**.
* File names should be of the format `$title.sql`.
  * For example, a file called `archaeology.sql` will create a network listed under the title "archaeology".

E.g. these are the contents of `last_30_days.sql`:

```sql
select id
from `covid-19-dimensions-ai.data.publications`
where 
EXTRACT(DATE FROM date_inserted) >= DATE_ADD(CURRENT_DATE(), INTERVAL -30 DAY)
```

### Network configuration

Network configuration options can be optionally defined in the SQL files before your query, as a series of commented lines starting with a predefined keyword. For example:

```sql
-- network_types: concepts, organizations
-- max_nodes: 400 
-- min_edge_weight: 3
-- min_concept_relevance: 0.5 
-- min_concept_frequency: 4

select id
from `covid-19-dimensions-ai.data.publications`
where 
EXTRACT(DATE FROM date_inserted) >= DATE_ADD(CURRENT_DATE(), INTERVAL -30 DAY)
and altmetrics.score > 1
```

If omitted, the default configuration values will be used. These are all the possible configurations and their meaning.

| Option                | Default               | Notes                                                                                                                                                                    |
|-----------------------|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| network_types         | concepts, organizations | Currenlty two network types are supported.                                                                                                                               |
| max_nodes             | 500                   | How many nodes should be displayed, at maximum?                                                                                                                          |
| min_edge_weight       | 3                     | How many edges should two nodes share before they are linked in the network?                                                                                             |
| min_concept_relevance | 0.5                   | Each concept tagged to a publication is assigned a relevance score between 0 and 1. What is the threshold that must be cleared before we consider a concept as relevant? |
| min_concept_frequency | 5                     | How many times should a concept appear in the corpus overall before it's included in the network?                                                                        |




## Output visualizations

Generated visualizations get added to the folder `user-outputs`, which is automatically created after running an extraction. 

The folder contains a static website consisting of HTML, JS and JSON assets. The website uses relative links hence it can be published on web server *as is*. For example, see the `/docs` folder in this repository, which is viewable at https://digital-science.github.io/dimensions-network-gen/index.html. 

In order to browse the output folder locally, run the server utility: `dimensions-network -s`. That will start a server on http://127.0.0.1:8009/


## Screenshots

A concept network:
![concepts-network](/screenshots/concepts-network.png)

An organization collaboration network:

![organizations-network.png](/screenshots/organizations-network.png)

