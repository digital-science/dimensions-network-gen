select id
from `covid-19-dimensions-ai.data.publications`
where 
"Italy" in UNNEST(research_org_country_names)