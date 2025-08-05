with airports as (
select distinct flap_iata_code, flap_country_iso_code  from l0_adiona.ex_flight_airport efa 
),
base as (
SELECT 
fpc_reference_product_id,fpc_iata_departure,fpc_iata_arrival,fpc_iata_return, count(*)
from l0_adiona.ex_flights_price_cached 
group by fpc_reference_product_id,fpc_iata_departure,fpc_iata_arrival,fpc_iata_return
)
select * from base left join airports  on base.fpc_iata_departure=airports.flap_iata_code
