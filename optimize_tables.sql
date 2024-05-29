-- Create a spatial index on the stops table
CREATE INDEX stops_geom_idx ON stops USING GIST (ST_SetSRID(ST_Point(stop_lon, stop_lat), 4326));

-- Create a spatial index on the route_stops table
CREATE INDEX route_stops_geom_idx ON route_stops USING GIST (ST_SetSRID(ST_Point(stop_lon, stop_lat), 4326));

-- Create a spatial index on the initial and final points of the taxi_services table
CREATE INDEX taxi_services_initial_point_idx ON taxi_services USING GIST (ST_Transform(initial_point, 3763));
CREATE INDEX taxi_services_final_point_idx ON taxi_services USING GIST (ST_Transform(final_point, 3763));