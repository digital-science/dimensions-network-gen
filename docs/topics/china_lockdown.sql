-- max_nodes: 400 
-- min_edge_weight: 2
-- min_concept_relevance: 0.5
-- min_concept_frequency: 2

SELECT
    id
FROM
    `covid-19-dimensions-ai.data.publications`
WHERE
    REGEXP_CONTAINS(
        title.preferred,
        r'chin.*lockdown|lockdown.*chin'
    ) OR 
        REGEXP_CONTAINS(
        abstract.preferred,
        r'chin.*lockdown|lockdown.*chin'
    )