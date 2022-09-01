
-- network_types: concepts, organizations
-- max_nodes: 300 
-- min_edge_weight: 2
-- min_concept_relevance: 0.6 
-- min_concept_frequency: 3

-- WARNING: this query uses full Dimensions data

select id
from `dimensions-ai.data_analytics.publications`
where 
REGEXP_CONTAINS(abstract.preferred, r'complexity.*science|science.*complexity')


