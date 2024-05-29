CREATE EXTENSION postgis;

CREATE TABLE route_stops (
    route_id VARCHAR(10),
    stop_id VARCHAR(10),
    stop_lat numeric(10,8),
    stop_lon numeric(10,8),
    direction_id NUMERIC(2),
    stop_sequence INTEGER
);

INSERT INTO route_stops (route_id, stop_id, stop_lat, stop_lon, direction_id, stop_sequence)
SELECT 
    tr.route_id, 
    st.stop_id,
    s.stop_lat,
    s.stop_lon,
    tr.direction_id,
    st.stop_sequence

FROM 
    stop_times st
JOIN 
    stops s
ON 
    s.stop_id = st.stop_id
JOIN 
    trips tr
ON st.trip_id = tr.trip_id
WHERE tr.service_id = 'UTEIS'
GROUP BY 
    tr.route_id, 
    st.stop_id,
    s.stop_lon,
    s.stop_lat,
    tr.direction_id,
    st.stop_sequence
;