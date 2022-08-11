from collections import defaultdict
import json
import urllib

from . import bqdata
from ..settings import *
from .helpers import *

import shutil 


def gen_orgs_collab_network(sql_file, config, fulldimensions=False, verbose=False):
    """
    Builds a collaboration network indicating links between organizations
    within the subset of publications defined by the user.

    Inputs:
      - topic (string): The name of the topic to be evaluated. Essentially
            just the input filename with the SQL extension stripped off.
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

    json_file_name = sql_file.split("/")[-1].replace(' ', '_').replace('.sql', '.json')
    render_vosviewer_json(data, 
        'Organizations', 
        'Publication',
        f"{DEFAULT_OUTPUT_JSON_PATH}/organizations/{json_file_name}",
        sql_file,
        )







def gen_concept_network(sql_file, config,  fulldimensions=False, verbose=False):
    """
    Builds a concept co-occurrence network indicating links between
    concepts, within the subset of publications defined by the user.

    Inputs:
      - topic: The name of the topic to be evaluated. Essentially
            just the input filename with the SQL extension stripped off.
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


    # 2022-05-13 TEST 
    # prefilling URLs using a template needed by vosviewer
    # filled with: %22Health%20Organization%22
    node_url = """https://app.dimensions.ai/discover/publication?search_text=%222019-nCoV%22%20OR%20%22COVID-19%22%20OR%20%E2%80%9CSARS-CoV-2%E2%80%9D%20OR%20%22HCoV-2019%22%20OR%20%22hcov%22%20OR%20%22NCOVID-19%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20coronavirus%202%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20corona%20virus%202%22%20OR%20%E2%80%9Ccoronavirus%20disease%202019%E2%80%9D%20OR%20((%22coronavirus%22%20OR%20%22corona%20virus%22)%20AND%20(Wuhan%20OR%20China%20OR%20novel))%20AND%20{id_url_safe}&search_type=kws&search_field=full_search&search_mode=content&or_facet_year=2022&or_facet_year=2021&or_facet_year=2020"""

    edge_url = """https://app.dimensions.ai/discover/publication?search_text=%222019-nCoV%22%20OR%20%22COVID-19%22%20OR%20%E2%80%9CSARS-CoV-2%E2%80%9D%20OR%20%22HCoV-2019%22%20OR%20%22hcov%22%20OR%20%22NCOVID-19%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20coronavirus%202%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20corona%20virus%202%22%20OR%20%E2%80%9Ccoronavirus%20disease%202019%E2%80%9D%20OR%20((%22coronavirus%22%20OR%20%22corona%20virus%22)%20AND%20(Wuhan%20OR%20China%20OR%20novel))%20AND%20{edge_url_safe}&search_type=kws&search_field=full_search&search_mode=content&or_facet_year=2022&or_facet_year=2021&or_facet_year=2020"""
    edge_url = """https://app.dimensions.ai/discover/publication?search_text=%222019-nCoV%22%20OR%20%22COVID-19%22%20OR%20%E2%80%9CSARS-CoV-2%E2%80%9D%20OR%20%22HCoV-2019%22%20OR%20%22hcov%22%20OR%20%22NCOVID-19%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20coronavirus%202%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20corona%20virus%202%22%20OR%20%E2%80%9Ccoronavirus%20disease%202019%E2%80%9D%20OR%20((%22coronavirus%22%20OR%20%22corona%20virus%22)%20AND%20(Wuhan%20OR%20China%20OR%20novel))%20AND%20{source_id_url}&search_type=kws&search_field=full_search&search_mode=content&or_facet_year=2022&or_facet_year=2021&or_facet_year=2020"""

    json_file_name = sql_file.split("/")[-1].replace(' ', '_').replace('.sql', '.json')
    render_vosviewer_json(data, 
                        'Concept', 
                        'Publication',
                        f"{DEFAULT_OUTPUT_JSON_PATH}/concepts/{json_file_name}",
                        sql_file,
                        node_url,
                        edge_url,
                        )







def render_vosviewer_json(data, node_label, link_label, outfile_name, sqlfile_path, node_url="", edge_url=""):
    """
    Shared function that accepts pairwise data returned from BigQuery and
    converts it into a VOSviewer JSON file.

    Inputs:
        - data (iterable): Results returned by GBQ. Each row is expected
            to include 5 elements: node1_id, node1_name, node2_id, node2_name,
            and a final integer indicating the strength of the link between
            node1 and node2.
        - node_label (string): What does a single node represent? Ex. "Organization"
        - link_label (string): What does a single link represent? Ex. "Publication"
        - outfile_name (string): Path to output file and location
    """

    edges = [] # links between two-concept combinations
    labels = {}

    try:
        for row in data:
            node1_id, node2_id, collabs = row
            edges.append((node1_id, node2_id, int(collabs)))
            labels[node1_id] = node1_id
            labels[node2_id] = node2_id
    except Exception:
        printDebug('  Error collating data for network.')
        raise

    # Data to be written
    towrite = {
        "config":{
            "terminology":{
                "item": node_label,
                "items": f"{node_label}s",
                "link": link_label,
                "links": f"{link_label}s",
                "link_strength": f"{link_label} links",
                "total_link_strength": "Total links"
            },
            "templates":{
                # SAMPLE
                # "item_description":"<div class='description_heading'>"+node_label+"</div><div class='description_label'><a class='description_url' href='https://app.dimensions.ai/discover/publication?facet_researcher={id}' target='_blank'>{label}</a></div>",
                # "link_description":"<div class='description_heading'>Publication links</div><div class='description_label'><a class='description_url' href='/vos/discover/publication?and_facet_researcher={source_id}' target='_blank'>{source_label}</a></div><div class='description_text'>{source_organization} - {source_address}</div><div class='description_label'><a class='description_url' href='/vos/discover/publication?and_facet_researcher={target_id}' target='_blank'>{target_label}</a></div><div class='description_text'>{target_organization} - {target_address}</div>",
                # DIMENSIONS LINKS FOR CONCEPTS
                "item_description":"<div class='description_heading'>"+node_label+"</div><div class='description_label'><a class='description_url' href='"+node_url+"' target='_blank'>{label}</a></div>",
                "link_description":"<div class='description_heading'>Publication links</div><div class='description_label'><a class='description_url' href='"+edge_url+"' target='_blank'>{source_label} + {target_label}</a></div>",
            },
            "styles":{
                "description_heading":"color: #757575; font-weight: 600;"
            }
        },
        "network":{
            "items":[],
            "links":[]
        }
    }

    # build network
    nodes = []


    try:
        for edge in edges:
            nodes.append(edge[0])
            nodes.append(edge[1])
            url_safe = urllib.parse.quote(f' "{edge[0]}" AND "{edge[1]}" ')
            url_safe = urllib.parse.quote(f'nothing')
            # "%22" + edge[0].replace(" ", "%20") + "%22%20%22" + edge[1].replace(" ", "%20") + "%22" 
            towrite['network']['links'].append({
                'source_id': edge[0],
                'target_id': edge[1],
                'source_id_url': url_safe, 
                'strength': edge[2]
            })
        nodes = list(set(nodes))
    except Exception:
        printDebug('Error when building list of nodes and edges.')
        raise

    for node in nodes:
        towrite['network']['items'].append({
            'id': node,
            'id_url_safe': "%22" + node.replace(" ", "%20") + "%22", # e.g.%22Health%20Organization%22
            'label': labels[node],
            # 'url': f"https://app.dimensions.ai/discover/publication?facet_researcher={node}",
            # 'description': f"""<a href="https://app.dimensions.ai/discover/publication?facet_researcher={node}">link</a>""",
        })

    printDebug(f"  => Nodes: {len(towrite['network']['items'])}. Edges: {len(towrite['network']['links'])}.", "important")
    if len(towrite['network']['items']):
        printDebug(f'  Writing network information to file:', "comment")
        printDebug(f'  ... {outfile_name}', "comment")
        with open(outfile_name, "w") as outfile:
            json.dump(towrite, outfile)

        # copy sql for doc purposes
        folder, filename = os.path.split(sqlfile_path)
        shutil.copyfile(sqlfile_path, f"{DEFAULT_OUTPUT_SQL_PATH}/{filename}")

    else:
        printDebug(f'  No nodes found - maybe review your query?', "red")


    printDebug('  Process complete.', "comment")



