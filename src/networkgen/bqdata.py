"""
Helper functions for interacting with BigQuery library
"""

from google.cloud import bigquery




class SendQueryError(Exception):
  """Exception raised for errors in sending DB queries

  Attributes:
    message -- explanation of the error
    query -- the query that was sent in the operation that returned the error
  """

  def __init__(self, message, query, params):
    self.message = message
    self.query = query
    self.params = params



class SendFileError(Exception):
  """Exception raised for errors in sending files to Cloud Storage

  Attributes:
    message -- explanation of the error
  """

  def __init__(self, message):
    self.message = message


class Client:
  
  def __init__(self, project=None, verbose=False):
    self.client = bigquery.Client()
    self.project = project
    self.verbose = verbose

  def send_query(self, q, params=None):
    """Constructs and sends a query to BigQuery.

    Parameters:
      q (str) -- The query to be submitted.
      params (list) -- A list of tuples describing query parameters
        to be substituted into the query string. Each tuple should
        be of the format (param_name, type, value). So a string
        parameter might be ("new_param", "STRING", "value_here")
        and an int might be ("new_paramval", "INT64", 250)

    Returns:
      results (list) -- A list of BigQuery Row() objects, which can
        be unpacked like a dictionary.
    """
    try:
      if params is None:
        query_job = self.client.query(q)  # Make an API request.
      else:
        #bigquery.ScalarQueryParameter("min_word_count", "INT64", 250)
        job_config = bigquery.QueryJobConfig(
          query_parameters=[bigquery.ScalarQueryParameter(*x) for x in params]
        )
        query_job = self.client.query(q, job_config=job_config)
        if self.verbose:
          print(f'---\nQUERY\n {query_job.query} \n---\n')

    except Exception as x:
      raise SendQueryError(x, q, params)
    else:
      return [x for x in query_job]


  def send_data(self, file, table_id, schema=None):
    """Opens a file and appends the results to a GBQ table.

    Parameters:
      file (str) -- Path to the file to be loaded
      table_id (str) -- The full name of the table where the new
        data should be appended. e.g. dimensions-dashboards-data.precalculated.pub_centrality
      params (list) -- A list of tuples describing query parameters
        to be substituted into the query string. Each tuple should
        be of the format (param_name, type, value). So a string
        parameter might be ("new_param", "STRING", "value_here")
        and an int might be ("new_paramval", "INT64", 250)

    Returns:
      kb (int) -- The size of the file that was loaded, in kilobytes
      rows (int) -- the number of rows written to the destination table
    """
    # Construct a BigQuery client object.

    job_config = bigquery.LoadJobConfig(
      schema=[bigquery.SchemaField(*x) for x in schema],
      write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
      source_format=bigquery.SourceFormat.CSV
    )

    try:
      with open(file, "rb") as source_file:
        job = self.client.load_table_from_file(source_file, table_id, job_config=job_config)
        job.result()  # Waits for the job to complete.
    except IOError as x:
      raise SendFileError(f'Could not open local file to send to GCP: {x}')
    except Exception as x:
      raise SendFileError(f'Unexpected error sending file to GCP: {x}')

    return (int(job.input_file_bytes / 1024), job.output_rows)
