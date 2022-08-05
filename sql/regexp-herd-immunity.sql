-- max_nodes: 400 
-- min_edge_weight: 2
-- min_concept_relevance: 0.6 
-- min_concept_frequency: 2

select id
from `covid-19-dimensions-ai.data.publications`
where 
REGEXP_CONTAINS(abstract.preferred, r'herd.*immunity|immunity.*herd')