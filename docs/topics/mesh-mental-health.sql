-- network_types: concepts, organizations
-- max_nodes: 300 
-- min_edge_weight: 2
-- min_concept_relevance: 0.7 
-- min_concept_frequency: 2

SELECT
    id
FROM
    `covid-19-dimensions-ai.data.publications`
WHERE
    "Mental Health" in UNNEST(mesh_headings)