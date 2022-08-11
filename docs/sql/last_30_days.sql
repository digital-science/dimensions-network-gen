-- network_types: concepts, organizations
-- max_nodes: 400 
-- min_edge_weight: 3
-- min_concept_relevance: 0.5 
-- min_concept_frequency: 4

select id
from `covid-19-dimensions-ai.data.publications`
where 
EXTRACT(DATE FROM date_inserted) >= DATE_ADD(CURRENT_DATE(), INTERVAL -30 DAY)
and altmetrics.score > 1