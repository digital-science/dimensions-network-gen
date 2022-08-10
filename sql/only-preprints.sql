-- network_types: concepts, organizations
-- max_nodes: 300 
-- min_edge_weight: 3
-- min_concept_relevance: 0.5 
-- min_concept_frequency: 5

select id
from `covid-19-dimensions-ai.data.publications`
where 
type="preprint"