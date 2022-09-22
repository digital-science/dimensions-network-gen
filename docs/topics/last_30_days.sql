-- Publications from last 30 days with an altmetric score > 10
-- network_types: concepts, organizations
-- max_nodes: 400 
-- min_edge_weight: 3
-- min_concept_relevance: 0.5 
-- min_concept_frequency: 4
SELECT
    id
FROM
    `covid-19-dimensions-ai.data.publications`
WHERE
    EXTRACT(
        DATE
        FROM
            date_inserted
    ) >= DATE_ADD(CURRENT_DATE(), INTERVAL -30 DAY)
    AND altmetrics.score > 10