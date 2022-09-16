-- AUTOMATICALLY GENERATED KEYWORD SEARCH QUERY
-- date: Sep-01-2022
-- max_nodes: 400 
-- min_edge_weight: 2
-- min_concept_relevance: 0.6
-- min_concept_frequency: 2
SELECT
    id
FROM
    `covid-19-dimensions-ai.data.publications`
WHERE
    REGEXP_CONTAINS(abstract.preferred, r'machine learning')
    OR REGEXP_CONTAINS(title.preferred, r'machine learning')