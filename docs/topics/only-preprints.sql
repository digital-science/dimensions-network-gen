-- network_types: concepts, organizations
-- max_nodes: 300 
-- min_edge_weight: 3
-- min_concept_relevance: 0.5 
-- min_concept_frequency: 5
SELECT
    id
FROM
    `covid-19-dimensions-ai.data.publications`
WHERE
    TYPE = "preprint"
    AND altmetrics.score > 5