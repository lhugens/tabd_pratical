import psycopg2
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime
import numpy as np

conn = psycopg2.connect(dbname = 'stcp', user = 'aluno', password = 'aluno')
cursor_psql = conn.cursor()

ids = {}
id = 0
sql = "SELECT trip_id from TRIPS;"
cursor_psql.execute(sql)
results = cursor_psql.fetchall()

scale_x = 0.1
scale_y = 0.01

#scale_x = 1/15000
#scale_y = 1/15000

#create point arrays
points_x = []
points_y = []
updates = []
transparency = []

#create ids for scatter arrays
id = 0
for s in results:
    ids[s[0]] = id
    id += 1
    updates.append([0, s[0]])

def query(t1, t2):
    sql = """ 
    SELECT
        --a.service_id,
        a.trip_id,
        --b.arrival_time,
        (max_stops.max_stop_sequence - b.stop_sequence) as difference,
        ST_AsText(ST_Transform(ST_SetSRID(ST_Point(c.stop_lon, c.stop_lat), 4326), 3763))
    FROM
        TRIPS a
    LEFT JOIN
        STOP_TIMES b ON a.trip_id = b.trip_id
    LEFT JOIN
        STOPS c ON b.stop_id = c.stop_id
    JOIN (
        SELECT trip_id, MAX(stop_sequence) AS max_stop_sequence
        FROM STOP_TIMES
        GROUP BY trip_id
    ) max_stops ON b.trip_id = max_stops.trip_id
    WHERE
        b.arrival_time >= '""" + t1 + """
        ' AND b.arrival_time < '""" + t2 + """' AND
        a.service_id = 'SABAGOST' 
        --AND a.trip_id = '500_0_U_69'
        AND a.route_id = '502'
    ;
    """
    cursor_psql.execute(sql)
    results = cursor_psql.fetchall()
    return results

def animate(i):
    global ax, points_x, points_y
    t = datetime.datetime(2000, 1, 1, 0, 30, 0) + datetime.timedelta(0, i * 10) #days, seconds
    t2 = t + datetime.timedelta(0, i * 10 + 10)
    print("time:", str(t.time(), t2.time()))
    results = query(str(t.time(), t2.time()))

    print(results)
    #points_x = []
    #points_y = []

    for p in results:
        p_str = p[0]
        p_id = ids[p_str]
        print(p_str, p_id)
        p_point = p[2][6:-1].split()
        p_x = float(p_point[0]) * scale_x
        p_y = float(p_point[1]) * scale_y

        print("point", p_id, p_x, p_y)

        points_x[p_id] = p_x        
        points_y[p_id] = p_y        
        transparency[p_id] = 1
    

    for (x, y) in zip(points_x, points_y):
        if(x != 0 or y != 0):
            print("point in list", x, y)
    
    #offsets = np.column_stack((points_x, points_y))

    # Update the scatter plot with the new offsets
    #scat.set_offsets(offsets)
    
    #print(points_x)
    #print(points_y)
    scat.set_offsets([points_x, points_y])
    #ax.scatter(points_x, points_y,s=len(points_x))

x_r = []
y_r = []
def make_arrays(t):
    global x_r, y_r, updates
    for i in range(t):
        t = datetime.datetime(2000, 1, 1, 7, 30, 0) + datetime.timedelta(0, i*10) #days, seconds
        t2 = t + datetime.timedelta(0, 10)
        print("time:", str(t.time()), str(t2.time()))

        xs = []
        ys = []

        for j in range(len(ids)):
            if(i > 0): xs.append(x_r[i-1][j])
            else: xs.append(0)
            if(i > 0): ys.append(y_r[i-1][j])
            else: ys.append(0)

        results = query(str(t.time()), str(t2.time()))
        for p in results:
            p_str = p[0]
            p_id = ids[p_str]

            #print(p)
            sequence = int(p[1])
            updates[p_id][0] += 1

            p_point = p[2][6:-1].split()
            p_x = float(p_point[0]) * scale_x
            p_y = float(p_point[1]) * scale_y
            #print("point", p_id, p_x, p_y)

            if(sequence == 0):
                print("sequence end")
                p_x = 0.0
                p_y = 0.0

            xs[p_id] = p_x        
            ys[p_id] = p_y       

        #xs[0] = -1000
        #ys[0] = 1000

        x_r.append(xs)
        y_r.append(ys)

def animate2(i):
    print("animate", i)
    #print(x_r[i][12432], y_r[i][12432])
    scat.set_offsets(np.column_stack((x_r[i], y_r[i])))
    #scat.set_offsets([x_r[i], y_r[i]])
    return scat,

for i in range(len(ids)):
    points_x.append(0)
    points_y.append(0)
    transparency.append(0)

frames = 6*60*24
frames = 6*60*4
make_arrays(frames)
#fig, ax = plt.subplots(figsize= (5000, 2000))
fig, ax = plt.subplots()
ax.set_xlim(-5000, -2900)
ax.set_ylim(1500, 1800)
scat = ax.scatter(x_r[0], y_r[0])
#animate(0)

anim = FuncAnimation( fig, animate2, frames = frames, interval=1, blit=True)

#for i in range(frames):
#    print(x_r[i][12432])

#anim.save("test.avi")
anim.save('animation.mp4', fps=60, writer='ffmpeg')
#animate(0)
#lt.draw()
#plt.show()

updates.sort(reverse=True)
print(updates[:1000])