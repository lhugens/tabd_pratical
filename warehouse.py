import psycopg2
import csv
from datetime import datetime

conn = psycopg2.connect("dbname=leo user=leo")
cursor_psql = conn.cursor()

file = open('trips.csv', 'w') 
writer = csv.writer(file)
writer.writerow(['initial_stop_id',
                                'initial_stop_point',
                                'route_id',
                                'initial_ts',
                                'final_stop_id',
                                'final_stop_point',
                                'final_ts'])

class Trip():
    def __init__(self, taxi_initial_point, taxi_initial_ts, taxi_final_point):
        self.writer = writer
        self.taxi_initial_point = taxi_initial_point
        self.taxi_initial_ts = taxi_initial_ts
        self.taxi_final_point = taxi_final_point

        self.bus_initial_stop_id = None
        self.bus_initial_stop_point = None
        self.bus_trip_id = None
        self.bus_initial_ts = None
        self.bus_final_stop_id = None
        self.bus_final_stop_point = None
        self.bus_final_ts = None
    
    def to_file(self):
        self.writer.writerow([self.bus_initial_stop_id,
                                self.bus_initial_stop_point,
                                self.bus_trip_id,
                                self.bus_initial_ts,
                                self.bus_final_stop_id,
                                self.bus_final_stop_point,
                                self.bus_final_ts])

trips = []

# all the texi trips: get initial_point, initial_ts, final_point
sql = '''
select st_transform(initial_point, 3763), 
        initial_ts, 
       st_transform(final_point, 3763)
from taxi_services
'''

cursor_psql.execute(sql)
results = cursor_psql.fetchall()
for initial_point, initial_ts, final_point in results:
    trips.append(Trip(initial_point, initial_ts, final_point))

# for each taxi trip, get bus info: initial_stop_id, initial_stop_point
for trip in trips[:5]:
    sql = f'''
        select stop_id, 
                st_transform(t.initial_point, 3763),
                st_transform(st_setsrid(st_point(s.stop_lon, s.stop_lat), 4326), 3763)
        from taxi_services t
        cross join stops s
        where st_transform(t.initial_point, 3763) = '{trip.taxi_initial_point}'
        order by st_distance(st_transform(st_setsrid(st_point(s.stop_lon, s.stop_lat), 4326),3763), '{trip.taxi_initial_point}')
        limit 1
    '''
    cursor_psql.execute(sql)
    results = cursor_psql.fetchall()
    #print(results)
    for stop_id, _, stop_point in results:
        trip.bus_initial_stop_id = stop_id
        trip.bus_initial_stop_point = stop_point
    # trip.to_file()

# for each initial_stop, query the routes that go by that stop at a later time than self.taxi_initial_ts
for trip in trips[:5]:
    ts = datetime.fromtimestamp(trip.taxi_initial_ts).time()
    sql = f'''
        select 
            st.departure_time
        from stop_times st
        join trips t on st.trip_id = t.trip_id
        where st.stop_id = '{trip.bus_initial_stop_id}'
        and st.departure_time > '{ts}'
        order by extract(epoch from (st.departure_time - '{ts}')) 
    '''

    cursor_psql.execute(sql)
    results = cursor_psql.fetchall()
    for row in results:
        print(row)