
-- network_types: concepts, collab_orgs
-- max_nodes: 300 
-- min_edge_weight: 2
-- min_concept_relevance: 0.5 
-- min_concept_frequency: 2

select id
from `covid-19-dimensions-ai.data.publications`
where 
journal.id = "jour.1018957"