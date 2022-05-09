select id
from `covid-19-dimensions-ai.data.publications`
where 
EXTRACT(DATE FROM date_inserted) >= DATE_ADD(CURRENT_DATE(), INTERVAL -30 DAY)