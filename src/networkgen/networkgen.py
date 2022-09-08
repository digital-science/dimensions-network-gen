from collections import defaultdict

from . import bqdata
from ..settings import *
from .helpers import *



def gen_orgs_collab_network(sql_file, config, fulldimensions=False, verbose=False):
    """
    Builds a collaboration network indicating links between organizations
    within the subset of publications defined by the user.

    Inputs:
      - sql_file (string): The input filename with the SQL topic query. Full path so that it can be read directly.
      - config (dict): Key-value pairs of configuration values required below.
    """

    db = bqdata.Client(verbose=verbose)
    DIMENSIONS_DATASET = gbq_dataset_name(fulldimensions)

    with open(sql_file, "r") as input:
        subquery = input.read()

    printDebug(f'Building organizations collaboration network..')
    printDebug(f'  File: {sql_file}', "comment")

    # fetch links
    q = f"""
    WITH subset AS (
        {subquery}
    ),
    top_nodes AS (
        SELECT orgid, COUNT(p.id) AS pubs
        FROM `{DIMENSIONS_DATASET}.publications` p
        CROSS JOIN UNNEST(p.research_orgs) orgid
        WHERE id IN (SELECT id FROM subset)
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT @max_nodes
    ),
    links AS (
        SELECT
        CONCAT(
            g1.name,
            ' (',
            # CONCAT(org1_id, " / type: ", ARRAY_TO_STRING(g1.types, ", ")),
            org1_id,
            ')'
        ) AS org1
        ,CONCAT(
            g2.name,
            ' (',
            # CONCAT(org2_id, " / type: ", ARRAY_TO_STRING(g2.types, ", ")),
            org2_id,
            ')'
        ) AS org2
        ,COUNT(DISTINCT p.id) AS collabs
        FROM `{DIMENSIONS_DATASET}.publications` p
        CROSS JOIN UNNEST(p.research_orgs) org1_id
        CROSS JOIN UNNEST(p.research_orgs) org2_id
        INNER JOIN `{DIMENSIONS_DATASET}.grid` g1
        ON org1_id=g1.id
        INNER JOIN `{DIMENSIONS_DATASET}.grid` g2
        ON org2_id=g2.id
        WHERE
        p.id IN (SELECT id FROM subset)
        AND org1_id > org2_id -- to prevent dupes
        AND org1_id IN (SELECT orgid FROM top_nodes)
        AND org2_id IN (SELECT orgid FROM top_nodes)
        GROUP BY 1,2
    )

    SELECT *
    FROM links
    WHERE collabs >= @min_edge_weight
    """

    params = [
        # ("topic", "STRING", topic),
        ("min_edge_weight", "INT64", config['min_edge_weight']),
        ("max_nodes", "INT64", config['max_nodes'])
    ]

    data = db.send_query(q, params=params)

    printDebug('  Network data retrieved from BigQuery.', "comment")

    return data




def gen_concept_network(sql_file, config,  fulldimensions=False, verbose=False):
    """
    Builds a concept co-occurrence network indicating links between
    concepts, within the subset of publications defined by the user.

    Inputs:
      - sql_file: The input filename with the SQL topic query. Full path so that it can be read directly.
      - config (dict): Key-value pairs of configuration values required below.
    """

    db = bqdata.Client(verbose=verbose)
    DIMENSIONS_DATASET = gbq_dataset_name(fulldimensions)

    with open(sql_file, "r") as input:
        subquery = input.read()

    printDebug(f'Building concept co-occurrence network..')
    printDebug(f'  File: {sql_file}', "comment")

    # fetch links
    q = f"""
        WITH subset AS (
            {subquery}
        ),
        papercount AS (
            SELECT concept.concept, COUNT(p.id) AS papers,
            FROM `{DIMENSIONS_DATASET}.publications` p
            INNER JOIN subset ON p.id=subset.id
            CROSS JOIN UNNEST(p.concepts) concept
            WHERE
                year >= 1965
                AND concept.relevance >= @min_link_relevance
            GROUP BY 1
        ),
        filtered AS (
            SELECT *
            FROM papercount
            WHERE papers >= @min_concept_frequency
            ORDER BY papers DESC
            LIMIT @max_nodes
        ),
        results AS (
        SELECT concept1.concept AS concept_a, concept2.concept AS concept_b,
            COUNT(p.id) AS overlap,
        FROM `{DIMENSIONS_DATASET}.publications` p
        INNER JOIN subset ON p.id=subset.id
        CROSS JOIN UNNEST(p.concepts) concept1
        CROSS JOIN UNNEST(p.concepts) concept2
        INNER JOIN filtered pcount1 ON concept1.concept=pcount1.concept
        INNER JOIN filtered pcount2 ON concept2.concept=pcount2.concept
        WHERE year >= 1965
            AND concept1.relevance >= @min_link_relevance
            AND concept2.relevance >= @min_link_relevance
            AND concept1.concept <> concept2.concept
        GROUP BY 1,2
        )
        SELECT *
        FROM results
        WHERE overlap >= @min_edge_weight
    """

    params = [
        ("max_nodes", "INT64", config['max_nodes']),
        ("min_edge_weight", "INT64", config['min_edge_weight']),
        ("min_link_relevance", "NUMERIC", config['min_concept_relevance']),
        ("min_concept_frequency", "INT64", config['min_concept_frequency']),
        # ("topic", "STRING", topic)
    ]

    data = db.send_query(q, params=params)

    printDebug('  Network data retrieved from BigQuery.', "comment")

    return data

