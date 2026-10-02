-- ====================================================================
-- Corporate Real Estate Portfolio & Workplace Analytics
-- Load Script: Ingest Clean CSV Data into Relational Tables
-- ====================================================================

-- Note: The Python DB loader (src/utilities/db_loader.py) executes this load
-- programmatically with strict type casting and foreign key verification.

-- Dimensions
COPY dim_geography FROM 'data/clean/dim_geography.csv' (HEADER, DELIMITER ',');
COPY dim_facility_type FROM 'data/clean/dim_facility_type.csv' (HEADER, DELIMITER ',');
COPY dim_property FROM 'data/clean/dim_property.csv' (HEADER, DELIMITER ',');
COPY dim_lease FROM 'data/clean/dim_lease.csv' (HEADER, DELIMITER ',');
COPY dim_floor FROM 'data/clean/dim_floor.csv' (HEADER, DELIMITER ',');
COPY dim_space FROM 'data/clean/dim_space.csv' (HEADER, DELIMITER ',');
COPY dim_date FROM 'data/clean/dim_date.csv' (HEADER, DELIMITER ',');

-- Facts
COPY fact_daily_workplace_utilization FROM 'data/clean/fact_daily_workplace_utilization.csv' (HEADER, DELIMITER ',');
COPY fact_room_utilization FROM 'data/clean/fact_room_utilization.csv' (HEADER, DELIMITER ',');
COPY fact_monthly_property_cost FROM 'data/clean/fact_monthly_property_cost.csv' (HEADER, DELIMITER ',');
COPY fact_headcount FROM 'data/clean/fact_headcount.csv' (HEADER, DELIMITER ',');
COPY fact_data_quality FROM 'data/clean/fact_data_quality.csv' (HEADER, DELIMITER ',');
