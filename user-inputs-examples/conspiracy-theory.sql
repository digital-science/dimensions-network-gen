select id
from `covid-19-dimensions-ai.data.publications`
where 
REGEXP_CONTAINS(abstract.preferred, r'conspiracy.*theory|theory.*conspiracy')