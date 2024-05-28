import psycopg2
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.colors as mcolors
from shapely.geometry import LineString, Point
from datetime import time, timedelta, datetime

class Route:
    def __init__(self, start, end, route):
            self.begin_time = start
            self.end_time = end
            self.route = route

class Stop:
    def __init__(self, time, sequence, x, y, id):
        self.time = time
        self.stop_sequence = sequence
        self.x = x 
        self.y = y 
        self.id = id
    

class Bus:
    def __init__(self, route_id, trip_id, shape_id):
        self.route_id = route_id
        self.trip_id = trip_id
        self.shape_id = shape_id
        self.stops = []
        self.routes = []

    def add_stop(self, stop):
         self.stops.append(stop)

    def add_route(self, route):
        self.routes.append(route)

    def map_f(self, t, t1, t2, d1, d2):
        return (((t - t1) * (d2 - d1)) / (t2 - t1)) + d1
    
    def get_t_seconds(self, t):
        return t.hour * 3600 + t.minute * 60 + t.second

    def next_position(self, t):
        for i in range(len(self.stops) - 1):
            if self.stops[i + 1].time >= t and self.stops[i].time < t:
                d1 = shapes_dic[self.shape_id].project(Point(self.stops[i].x, self.stops[i].y))
                d2 = shapes_dic[self.shape_id].project(Point(self.stops[i+1].x, self.stops[i+1].y))
                t1 = self.get_t_seconds(self.stops[i].time)
                t2 = self.get_t_seconds(self.stops[i+1].time)
                t = self.get_t_seconds(t)
                d = self.map_f(t, t1, t2, d1, d2)
                #print(self.stops[i].id)
                return shapes_dic[self.shape_id].interpolate(d)
        return Point(0,0)


conn = psycopg2.connect(dbname = 'stcp', user = 'aluno', password = 'aluno')
cursor_psql = conn.cursor()

plt.style.use('dark_background')
#plt.style.use('default')
xmin = -49964.492999999784
xmax = -25724.446600000374
ymin = 155509.45260000043
ymax = 180795.91699999943

scale = 1/30000
width_in_inches = ((xmax - xmin)/0.0254)*1.1
height_in_inches = ((ymax - ymin)/0.0254)*1.1

#fig = plt.figure(figsize=(width_in_inches*scale, height_in_inches*scale))
#scat = plt.scatter([], [], color='red')

fig, ax = plt.subplots()
scat = ax.scatter([], [], s = 2, color = 'red', alpha=1)
#scat = ax.scatter([], [], color = 'red', alpha=1)
#fig.set_figheight(height_in_inches*scale)
#fig.set_figwidth(width_in_inches*scale)
ax.set_xlim(-50500, -25000)
ax.set_ylim(155000, 182000)

busses = {}
shapes_dic = {}

service_time = "DOMVERAO"
sql_query_find_busses = '''
SELECT route_id, trip_id, shape_id 
FROM trips
WHERE service_id = '{}'
--AND route_id = '500'
--LIMIT 1
;
'''.format(service_time)

cursor_psql.execute(sql_query_find_busses)
results = cursor_psql.fetchall()

for p in results:
    busses[str(p[1])] = Bus(p[0], p[1], p[2])

print(len(busses))

sql_query_find_stops_for_bus = '''
SELECT 
b.trip_id,
b.arrival_time, 
(max_stop_sequence - b.stop_sequence) as difference,
ST_AsText(ST_Transform(ST_SetSRID(ST_Point(c.stop_lon, c.stop_lat), 4326), 3763)),
c.stop_name
FROM stop_times b
LEFT JOIN
    stops c ON b.stop_id = c.stop_id
JOIN (
        SELECT trip_id, MAX(stop_sequence) AS max_stop_sequence
        FROM STOP_TIMES
        GROUP BY trip_id
    ) max_stops ON b.trip_id = max_stops.trip_id
;
'''

cursor_psql.execute(sql_query_find_stops_for_bus)
results = cursor_psql.fetchall()

for p in results:
    (x,y) = p[3][6:-1].split()
    stop = Stop(p[1], p[2], float(x), float(y), p[4])
    if str(p[0]) in busses:
        busses[str(p[0])].add_stop(stop)
        #print(p)

for b in busses.values():
    b.stops.sort(key=lambda Stop: Stop.stop_sequence, reverse=True)

#make routes for every bus
for b in busses.values():
    res = 0
    if(b.shape_id not in shapes_dic):
        arr = []

        sql_query_get_shape_line = '''
        SELECT ST_AsText(ST_Collect(ST_Transform(ST_SetSRID(ST_Point(shape_pt_lon, shape_pt_lat), 4326), 3763)))
        FROM shapes
        WHERE shape_id = '{}'
        ;
        '''.format(b.shape_id)

        cursor_psql.execute(sql_query_get_shape_line)
        results = cursor_psql.fetchall()

        points = []
        results = results[0][0][11:-1]
        print(results)
        for p in results.split(','):
            (x,y) = p.split()
            points.append((float(x), float(y)))

        shapes_dic[b.shape_id] = LineString(points) 
        print(shapes_dic[b.shape_id])

        #print(stop1.id, stop2.id, b.shape_id, b.trip_id)
        #print(results)
        res += 1

sql = """
select st_astext(st_simplify(proj_boundary,10))
from cont_aad_caop2018
join (
select st_transform(st_setsrid(st_point(stop_lon, stop_lat), 4326), 3763) as geom
from stops
) as transformed_geom on st_contains(proj_boundary, transformed_geom.geom)
where distrito = 'PORTO';
"""

cursor_psql.execute(sql)
results = cursor_psql.fetchall()

for row in results:
    xs = []
    ys = []
    points_string = row[0]
    points_string = points_string[9:-2].split(",")
    for point in points_string:
        (x,y) = point.split()
        xs.append(float(x))
        ys.append(float(y))
    plt.plot(xs,ys, color='yellow',linewidth=0.2)
    #plt.plot(xs,ys,linewidth=0.2)

######################### 
# plot the bus routes
######################### 

ids = {}
id = 0
sql = "SELECT shape_id from shapes;"
cursor_psql.execute(sql)
results = cursor_psql.fetchall()

shapes = []

id = 0
for s in results:
    ids[s[0]] = id
    id += 1
    shapes.append([])

sql = """
select shape_id, 
st_astext(st_transform(st_setsrid(st_point(shape_pt_lon, shape_pt_lat), 4326), 3763)) as geometry,
shape_pt_sequence
from shapes
"""
cursor_psql.execute(sql)
results = cursor_psql.fetchall()

dic = {}
dic_id = 0

for result in results:
    id_p = result[0]
    id_s = ids[id_p]
    sequence = int(result[2])
    ps = result[1][6:-1].split()
    x = float(ps[0])
    y = float(ps[1])
    shapes[id_s].append((sequence,x,y))

for s in shapes:
    s = sorted(s,key=lambda x:s[0])

#for row in shapes:
    #xs = []
    #ys = []
    #for p in row:
        #x = float(p[1])
        #y = float(p[2])
        #xs.append(x)
        #ys.append(y)
    #plt.plot(xs,ys,color='gray',alpha=0.2)
    #plt.plot(xs,ys,alpha=0.2)

def animate(t):
    print("Animate", t)
    t = datetime(2000,1,1, 8, 0, 0) + timedelta(seconds = t)
    x = []
    y = []
    for b in busses.values():
        p = b.next_position(t.time())
        if p != Point(0,0):
            x.append(p.x)
            y.append(p.y)
    scat.set_offsets(np.column_stack((x, y)))
    return scat,

frames = 3600 * 12
#frames = 60

anim = FuncAnimation( fig, animate, frames = frames, interval=1, blit=True)
anim.save('animation.mp4', fps=60, writer='ffmpeg')