-- Highly cited papers from Chinese authors
-- max_nodes: 400 
-- min_edge_weight: 2
-- min_concept_relevance: 0.7 
-- min_concept_frequency: 2
SELECT
    id
FROM
    `covid-19-dimensions-ai.data.publications`
WHERE
    "China" IN UNNEST(research_org_country_names)
    AND metrics.times_cited >= 50