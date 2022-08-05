-- max_nodes: 400 
-- min_edge_weight: 2
-- min_concept_relevance: 0.7 
-- min_concept_frequency: 2


select id
from `covid-19-dimensions-ai.data.publications`
where 
"Italy" in UNNEST(research_org_country_names)