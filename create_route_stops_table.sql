CREATE EXTENSION postgis;

DROP TABLE route_stops;

CREATE TABLE route_stops (
    route_id VARCHAR(10),
    stop_id VARCHAR(10),
    stop_lat numeric(10,8),
    stop_lon numeric(10,8),
    direction_id NUMERIC(2),
    stop_sequence INTEGER,
    last_departure TIME,
    trip_headsign VARCHAR(50),
    trip_headsign_hash INTEGER,
    max_sequence INTEGER
    --add last departure_time to minimize fails
);

CREATE INDEX idx_max_sequence ON route_stops (max_sequence);
CREATE INDEX idx_hash ON route_stops (trip_headsign_hash);
CREATE INDEX idx_sequence ON route_stops (stop_sequence);
-- Create a spatial index on the route_stops table
CREATE INDEX route_stops_geom_idx ON route_stops USING GIST (ST_SetSRID(ST_Point(stop_lon, stop_lat), 4326));

--INSERT INTO route_stops (route_id, stop_id, stop_lat, stop_lon, direction_id, stop_sequence)
--SELECT 
    --tr.route_id, 
    --st.stop_id,
    --s.stop_lat,
    --s.stop_lon,
    --tr.direction_id,
    --st.stop_sequence

--FROM 
    --stop_times st
--JOIN 
    --stops s
--ON 
    --s.stop_id = st.stop_id
--JOIN 
    --trips tr
--ON st.trip_id = tr.trip_id
--WHERE tr.service_id = 'UTEIS'
--GROUP BY 
    --tr.route_id, 
    --st.stop_id,
    --s.stop_lon,
    --s.stop_lat,
    --tr.direction_id,
    --st.stop_sequence
--;

INSERT INTO route_stops (route_id, stop_id, stop_lat, stop_lon, direction_id, stop_sequence, last_departure, trip_headsign, trip_headsign_hash, max_sequence)
WITH max_st AS (
    SELECT trip_id, MAX(stop_sequence) as max_seq
    FROM stop_times
    GROUP BY trip_id
)
SELECT 
    tr.route_id, 
    st.stop_id,
    s.stop_lat,
    s.stop_lon,
    tr.direction_id,
    st.stop_sequence,
    MAX(st.departure_time) AS max_departure_time,
    tr.trip_headsign,
    hashtext(tr.trip_headsign),
    max_st.max_seq
FROM 
    stop_times st
JOIN 
    stops s
ON 
    s.stop_id = st.stop_id
JOIN 
    trips tr
ON 
    st.trip_id = tr.trip_id
JOIN max_st 
ON max_st.trip_id = st.trip_id
    --AND tr.service_id = 'UTEIS'
WHERE tr.service_id = 'UTEIS'
GROUP BY 
    tr.route_id, 
    st.stop_id,
    s.stop_lon,
    s.stop_lat,
    tr.direction_id,
    tr.trip_headsign,
    max_st.max_seq,
    st.stop_sequence;