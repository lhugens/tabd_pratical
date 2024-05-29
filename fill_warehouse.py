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
FROM trips t;
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
    SELECT trip_id, stop_id, departure_time 
    FROM stop_times;
'''

cursor_psql.execute(sql_get_stop_times)
results = cursor_psql.fetchall()

for r in results:
    if trip_stop_times.get(r[0]) == None:
        trip_stop_times[r[0]] = {}
    trip_stop_times[r[0]][r[1]] = r[2]

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------
    
main_query = ''' 
SELECT
    --t.id,
    s.route_id,
    s.init_stop_id,
    s.end_stop_id,
    st_astext(st_transform(t.initial_point, 3763)) as initial_point,
    st_astext(st_transform(t.final_point, 3763)) as final_point,
    st_astext(st_transform(st_setsrid(st_point(s.init_lon, s.init_lat), 4326), 3763)) as stop_point_init,
    st_astext(st_transform(st_setsrid(st_point(s.end_lon, s.end_lat), 4326), 3763)) as stop_point_end,
    t.initial_ts,
    t.final_ts
FROM taxi_services t
JOIN LATERAL (
    WITH p1 AS (
        SELECT 
            stop_id
        FROM 
            stops s
        ORDER BY 
            ST_Distance(
                ST_Transform(ST_SetSRID(ST_Point(s.stop_lon, s.stop_lat), 4326), 3763), 
                ST_Transform(t.initial_point, 3763)
            )
        LIMIT 5
    ),
    p2 AS (
        SELECT DISTINCT ON (rs.route_id, rs.direction_id)
            rs.route_id,
            rs.direction_id,
            rs.stop_sequence,
            p1.stop_id,
            rs.stop_lon,
            rs.stop_lat
        FROM 
            route_stops rs
        JOIN p1 
        ON rs.stop_id = p1.stop_id
        GROUP BY
            rs.route_id,
            rs.direction_id,
            rs.stop_sequence,
            p1.stop_id,
            rs.stop_lon,
            rs.stop_lat
    )
    SELECT
        p2.stop_id as init_stop_id,
        p2.stop_lat as init_lat,
        p2.stop_lon as init_lon,
        rs.stop_id as end_stop_id,
        rs.stop_lat as end_lat,
        rs.stop_lon as end_lon,
        rs.route_id
    FROM
        route_stops rs
    JOIN
        p2
    ON rs.route_id = p2.route_id
    WHERE
        p2.direction_id = rs.direction_id
        AND p2.stop_sequence < rs.stop_sequence
    GROUP BY 
        p2.stop_id,
        p2.stop_lat,
        p2.stop_lon,
        rs.stop_id,
        rs.stop_lat,
        rs.stop_lon,
        rs.route_id
    ORDER BY 
        ST_Distance(
            ST_ClosestPoint(
                ST_Collect(ST_Transform(ST_SetSRID(ST_Point(rs.stop_lon, rs.stop_lat), 4326), 3763)),
                ST_Transform(t.final_point, 3763)
            ), 
            ST_Transform(t.final_point, 3763)
        )
        --ordenar pela soma das distancias
        
    LIMIT 1
) AS s ON TRUE
LIMIT 100
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

for t in trips:
    trip = ''
    best_init_time = -1
    best_time_found = False

    t_init = datetime.fromtimestamp(t.taxi_init_time).time()

    for tr in trips_in_routes[t.route_id]:
        if(trip_stop_times.get(tr) == None): continue
        if(trip_stop_times[tr].get(t.bus_init_stop) == None): continue
        if(trip_stop_times[tr].get(t.bus_end_stop) == None): continue

        if(trip_stop_times[tr][t.bus_init_stop] > t_init):
            if(best_time_found):
                if trip_stop_times[tr][t.bus_init_stop] < best_init_time:
                    best_init_time = trip_stop_times[tr][t.bus_init_stop]
                    trip = tr
            else:
                best_init_time = trip_stop_times[tr][t.bus_init_stop]
                best_time_found = 1
                trip = tr
    t_end = -1

    if(trip != ''):
        #print("trip", trip, "end stop", t.bus_end_stop)
        t_end = trip_stop_times[trip][t.bus_end_stop]
        t.set_times(trip, best_init_time, t_end)
    else:
        print("trip time", t_init, "begin stop:", t.bus_init_stop, "end stop:", t.bus_end_stop, "route", t.route_id)

trips = [t for t in trips if t.trip_id != -1]

#-------------------------------------------------
#-------------------------------------------------
#-------------------------------------------------

#create sql file with all rows
    
with open("fill_warehouse.sql", "w+") as f:
    for t in trips:
        print(t, file=f)

