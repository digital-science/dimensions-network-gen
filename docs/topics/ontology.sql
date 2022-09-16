
-- AUTOMATICALLY GENERATED KEYWORD SEARCH QUERY
-- date: Aug-12-2022
-- max_nodes: 400 
-- min_edge_weight: 1
-- min_concept_relevance: 0.5
-- min_concept_frequency: 2

select id
from `covid-19-dimensions-ai.data.publications`
where 
REGEXP_CONTAINS(abstract.preferred, r'ontology')
OR
REGEXP_CONTAINS(title.preferred, r'ontology')
    