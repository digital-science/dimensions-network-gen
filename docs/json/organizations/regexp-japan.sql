
-- network_types: concepts, organizations
-- max_nodes: 400 
-- min_edge_weight: 1
-- min_concept_relevance: 0.4
-- min_concept_frequency: 2

select id
from `covid-19-dimensions-ai.data.publications`
where 
REGEXP_CONTAINS(abstract.preferred, r'japan')
OR
REGEXP_CONTAINS(title.preferred, r'japan')