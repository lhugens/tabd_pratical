import psycopg2
import matplotlib.pyplot as plt
from datetime import datetime


class Trip:
    def __init__(self, route_id, bus_init_stop, bus_end_stop, taxi_init_pos, taxi_end_pos, bus_init_pos, bus_end_pos, taxi_init_time, taxi_end_time):
        self.route_id = route_id
        
        self.bus_init_stop = bus_init_stop
        self.bus_end_stop = bus_end_stop

        self.taxi_init_pos = taxi_init_pos
        self.taxi_end_pos = taxi_end_pos



        self.bus_init_pos = bus_init_pos
        self.bus_end_pos = bus_end_pos

        self.taxi_init_time = taxi_init_time
        self.taxi_end_time = taxi_end_time

        self.trip_id = -1

    def set_times(self, trip_id, init_time, end_time):
        self.trip_id = trip_id
        self.bus_init_time = init_time
        self.bus_end_time = end_time

    def __str__(self):
        return "insert into warehouse values ( '{}', '{}', '{}', '{}', {}, {}, '{}', '{}', '{}', '{}', '{}', '{}' );".format(
            self.route_id,
            self.trip_id,
            self.bus_init_stop,
            self.bus_end_stop, 
            self.taxi_init_time,
            self.taxi_end_time,
            self.bus_init_time,
            self.bus_end_time,
            self.taxi_init_pos,
            self.taxi_end_pos,
            self.bus_init_pos,
            self.bus_end_pos
        )

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

#connection

conn = psycopg2.connect("dbname=leo user=leo")
cursor_psql = conn.cursor()

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

#build a dictionary of the type dic[route_id] = [trip_id] 
trips_in_routes = {}

sql_get_trips_from_routes = ''' 
SELECT
    route_id, 
    trip_id
FROM trips t
WHERE service_id = 'UTEIS'
'''
cursor_psql.execute(sql_get_trips_from_routes)
results = cursor_psql.fetchall()

for r in results:
    if trips_in_routes.get(r[0]) == None:
        trips_in_routes[r[0]] = []
    trips_in_routes[r[0]].append(r[1])

#-------------------------------------------------

#build a dictionary of the type dic[trip_id][stop_id] = departure_time
trip_stop_times = {}

sql_get_stop_times = ''' 
    SELECT st.trip_id, stop_id, departure_time 
    FROM stop_times st
    JOIN trips t
    ON st.trip_id = t.trip_id
    WHERE t.service_id = 'UTEIS'
    ;
'''

cursor_psql.execute(sql_get_stop_times)
results = cursor_psql.fetchall()

for r in results:
    if trip_stop_times.get(r[0]) == None:
        trip_stop_times[r[0]] = {}
    if trip_stop_times[r[0]].get(r[1]) == None:
        trip_stop_times[r[0]][r[1]] = []
    trip_stop_times[r[0]][r[1]].append(r[2])

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

main_query = ''' 
SELECT
    s.route_id,
    s.init_stop_id,
    s.end_stop_id,
    ST_AsText(ST_Transform(t.initial_point, 3763)) AS initial_point,
    ST_AsText(ST_Transform(t.final_point, 3763)) AS final_point,
    ST_AsText(ST_Transform(ST_SetSRID(ST_Point(s.init_lon, s.init_lat), 4326), 3763)) AS stop_point_init,
    ST_AsText(ST_Transform(ST_SetSRID(ST_Point(s.end_lon, s.end_lat), 4326), 3763)) AS stop_point_end,
    CAST(TO_TIMESTAMP(t.initial_ts) AS TIME),
    CAST(TO_TIMESTAMP(t.final_ts) AS TIME)
FROM taxi_services t
JOIN LATERAL (
    WITH p1 AS (
        SELECT 
            stop_id,
            stop_lat,
            stop_lon
        FROM 
            stops
        ORDER BY 
            ST_Distance(
                ST_Transform(ST_SetSRID(ST_Point(stop_lon, stop_lat), 4326), 3763), 
                ST_Transform(t.initial_point, 3763)
            )
        LIMIT 5
    ),
    p2 AS (
        SELECT DISTINCT ON (rs.route_id, rs.direction_id)
            rs.route_id,
            rs.direction_id,
            rs.stop_sequence,
            rs.max_sequence,
            rs.trip_headsign_hash,
            p1.stop_id,
            rs.stop_lon,
            rs.stop_lat
        FROM 
            route_stops rs
        JOIN p1 
        ON rs.stop_id = p1.stop_id
        WHERE CAST(TO_TIMESTAMP(t.initial_ts) AS TIME) <= rs.last_departure
    ),
    s AS (
        SELECT
            p2.stop_id AS init_stop_id,
            p2.stop_lat AS init_lat,
            p2.stop_lon AS init_lon,
            rs.stop_id AS end_stop_id,
            rs.stop_lat AS end_lat,
            rs.stop_lon AS end_lon,
            rs.route_id
        FROM
            route_stops rs
        JOIN
            p2
        ON rs.route_id = p2.route_id 
        WHERE
            p2.direction_id = rs.direction_id
            AND p2.trip_headsign_hash = rs.trip_headsign_hash
            AND p2.stop_sequence < rs.stop_sequence
            AND p2.max_sequence = rs.max_sequence
            AND CAST(TO_TIMESTAMP(t.final_ts) AS TIME) <= rs.last_departure
        ORDER BY 
            ST_Distance(
                ST_Transform(ST_SetSRID(ST_Point(rs.stop_lon, rs.stop_lat), 4326), 3763),
                ST_Transform(t.final_point, 3763)
            )
        LIMIT 1
    )
    SELECT
        s.route_id,
        s.init_stop_id,
        s.end_stop_id,
        s.init_lat,
        s.init_lon,
        s.end_lat,
        s.end_lon
    FROM s

) AS s ON TRUE
LIMIT 100000;
'''

results = []
cursor_psql.execute(main_query)
results = cursor_psql.fetchall()

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

#create trips array
trips = []

for r in results:
    trips.append(Trip(*r)) # * unpacks the array

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

#get stop times

failed_data_points = 0

for t in trips:
    trip = ''
    best_time_found = False
    best_init = -1
    best_end = -1

    #print(t.taxi_init_time)
    t_init = t.taxi_init_time
    for tr in trips_in_routes[t.route_id]:
        if(trip_stop_times.get(tr) == None): continue
        if(trip_stop_times[tr].get(t.bus_init_stop) == None): continue
        if(trip_stop_times[tr].get(t.bus_end_stop) == None): continue


        for init in trip_stop_times[tr][t.bus_init_stop]:
            for end in trip_stop_times[tr][t.bus_end_stop]:
                #print(init, end)
                if(init > t_init):
                    if(init < end):
                        if(best_time_found):
                            if init < best_init and end < best_end:
                            #if end < best_end:
                                best_init = init
                                best_end = end
                                trip = tr
                        else:
                            best_init = init
                            best_end = end
                            best_time_found = 1
                            trip = tr


    if(trip != ''):
        if(best_end < best_init):
            #print("error", trip, best_init, best_end)
            #print("trip time", t_init, "begin stop:", t.bus_init_stop, "end stop:", t.bus_end_stop, "route", t.route_id)
            failed_data_points += 1
            continue
        t.set_times(trip, best_init, best_end)
    else:
        #print("trip time", t_init, "begin stop:", t.bus_init_stop, "end stop:", t.bus_end_stop, "route", t.route_id, "trip", t.trip_id)
        failed_data_points += 1

trips = [t for t in trips if t.trip_id != -1]

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

#create sql file with all rows
    
with open("fill_warehouse.sql", "w+") as f:
    for t in trips:
        print(t, file=f)

#for t in trips:
    #print(t)

print("failed entries", failed_data_points)