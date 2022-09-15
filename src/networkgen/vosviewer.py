import json
import urllib
import shutil 

from ..settings import *
from .helpers import *





def get_concepts_node_urls():
    """Temp helpers to create nicely readable URLs for concepts co-occurrence charts"""

    # 2022-05-13 TEST 
    # prefilling URLs using a template needed by vosviewer
    # filled with: %22Health%20Organization%22
    node_url = """https://app.dimensions.ai/discover/publication?search_text=%222019-nCoV%22%20OR%20%22COVID-19%22%20OR%20%E2%80%9CSARS-CoV-2%E2%80%9D%20OR%20%22HCoV-2019%22%20OR%20%22hcov%22%20OR%20%22NCOVID-19%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20coronavirus%202%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20corona%20virus%202%22%20OR%20%E2%80%9Ccoronavirus%20disease%202019%E2%80%9D%20OR%20((%22coronavirus%22%20OR%20%22corona%20virus%22)%20AND%20(Wuhan%20OR%20China%20OR%20novel))%20AND%20{id_url_safe}&search_type=kws&search_field=full_search&search_mode=content&or_facet_year=2022&or_facet_year=2021&or_facet_year=2020"""

    edge_url = """https://app.dimensions.ai/discover/publication?search_text=%222019-nCoV%22%20OR%20%22COVID-19%22%20OR%20%E2%80%9CSARS-CoV-2%E2%80%9D%20OR%20%22HCoV-2019%22%20OR%20%22hcov%22%20OR%20%22NCOVID-19%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20coronavirus%202%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20corona%20virus%202%22%20OR%20%E2%80%9Ccoronavirus%20disease%202019%E2%80%9D%20OR%20((%22coronavirus%22%20OR%20%22corona%20virus%22)%20AND%20(Wuhan%20OR%20China%20OR%20novel))%20AND%20{edge_url_safe}&search_type=kws&search_field=full_search&search_mode=content&or_facet_year=2022&or_facet_year=2021&or_facet_year=2020"""

    edge_url = """http://app.dimensions.ai{id_url_safe}"""   

    return node_url, edge_url





def get_concepts_node_urls():
    """Temp helpers to create nicely readable URLs for concepts co-occurrence charts"""

    # 2022-05-13 TEST 
    # prefilling URLs using a template needed by vosviewer
    # filled with: %22Health%20Organization%22
    node_url = """https://app.dimensions.ai/discover/publication?search_text=%222019-nCoV%22%20OR%20%22COVID-19%22%20OR%20%E2%80%9CSARS-CoV-2%E2%80%9D%20OR%20%22HCoV-2019%22%20OR%20%22hcov%22%20OR%20%22NCOVID-19%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20coronavirus%202%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20corona%20virus%202%22%20OR%20%E2%80%9Ccoronavirus%20disease%202019%E2%80%9D%20OR%20((%22coronavirus%22%20OR%20%22corona%20virus%22)%20AND%20(Wuhan%20OR%20China%20OR%20novel))%20AND%20{id_url_safe}&search_type=kws&search_field=full_search&search_mode=content&or_facet_year=2022&or_facet_year=2021&or_facet_year=2020"""

    edge_url = """https://app.dimensions.ai/discover/publication?search_text=%222019-nCoV%22%20OR%20%22COVID-19%22%20OR%20%E2%80%9CSARS-CoV-2%E2%80%9D%20OR%20%22HCoV-2019%22%20OR%20%22hcov%22%20OR%20%22NCOVID-19%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20coronavirus%202%22%20OR%20%22severe%20acute%20respiratory%20syndrome%20corona%20virus%202%22%20OR%20%E2%80%9Ccoronavirus%20disease%202019%E2%80%9D%20OR%20((%22coronavirus%22%20OR%20%22corona%20virus%22)%20AND%20(Wuhan%20OR%20China%20OR%20novel))%20AND%20{edge_url_safe}&search_type=kws&search_field=full_search&search_mode=content&or_facet_year=2022&or_facet_year=2021&or_facet_year=2020"""

    edge_url = """http://app.dimensions.ai{id_url_safe}"""   

    return node_url, edge_url
    


def render_json(data, task, node_label, link_label, sql_file, node_url="", edge_url=""):
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
        - sql_file (string): Path to SQL file
        - node_url (string):
        - edge_url (string):

    About hyperlinks:
    For some reason the edges URLs can be added to the JSON directly via the `url` key, however that does not work with nodes.
    Hence with nodes we have to use a config/template structure, and pass a variable `custom_search` into the JSON which is then resolved in the front end JS layer. 

    TODO: clarify with https://app.vosviewer.com/docs/ folks 
    """

    edges = [] # links between two-concept combinations
    labels = {}
    outfile_name = sql_file.split("/")[-1].replace(' ', '_').replace('.sql', '.json')
    outfile_name = f"{DEFAULT_OUTPUT_JSON_PATH}/{task}/{outfile_name}"

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
                # DIMENSIONS LINKS: NODES
                "item_description":"<div class='description_heading'>"+node_label+"</div><div class='description_label'><a class='description_url' href='"+BASE_DIMENSIONS_URL+"' target='_blank'>{label}</a></div>",
                # DIMENSIONS LINKS: EDGES
                "link_description":"<div class='description_heading'>"+link_label+"</div><div class='description_label'>{source_label} + {target_label}</div>"
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

    # EDGES

    try:
        for edge in edges:
            nodes.append(edge[0])
            nodes.append(edge[1])
            url_safe = "http://www.app.dimensions.ai"
            
            if task == "concepts":
                url_safe = "%20AND%20%22" + edge[0].replace(" ", "%20") + "%20AND%20" + edge[1].replace(" ", "%20") + "%22"
            
            elif task == "organizations":
                grid_id1 = edge[0][edge[0].index("grid"):-1]
                grid_id2 = edge[1][edge[1].index("grid"):-1]
                # url_safe = urllib.parse.quote(f' "{edge[0]}" AND "{edge[1]}" ')
                url_safe = f"&and_facet_research_org={grid_id1}&and_facet_research_org={grid_id2}"
            
            towrite['network']['links'].append({
                'source_id': edge[0],
                'target_id': edge[1],
                'url': BASE_DIMENSIONS_URL.format(custom_search=url_safe), 
                'strength': edge[2]
            })
        nodes = list(set(nodes))
    except Exception:
        printDebug('Error when building list of nodes and edges.')
        raise

    # NODES

    for node in nodes:
        if task == "concepts":
            extra_string = "%20AND%20%22" + node.replace(" ", "%20") + "%22"

        elif task == "organizations":    
            # org nodes are formatted as "King's College London (grid.13097.3c)"
            grid_id = node[node.index("grid"):-1]
            extra_string = f"&and_facet_research_org={grid_id}"

        towrite['network']['items'].append({
            'id': node,
            'custom_search': extra_string, # e.g.%22Health%20Organization%22
            'label': labels[node],
        })

    # Finally, save the JSON file

    printDebug(f"  => Nodes: {len(towrite['network']['items'])}. Edges: {len(towrite['network']['links'])}.", "important")
    if len(towrite['network']['items']):
        printDebug(f'Writing network information to file:', "comment")
        printDebug(f'  ... {outfile_name}', "comment")
        with open(outfile_name, "w") as outfile:
            json.dump(towrite, outfile)

        # copy sql for doc purposes
        folder, filename = os.path.split(sql_file)
        shutil.copyfile(sql_file, f"{DEFAULT_OUTPUT_SQL_PATH}/{filename}")

    else:
        printDebug(f'  No nodes found - maybe review your query?', "red")


    printDebug('  Process complete.', "comment")




