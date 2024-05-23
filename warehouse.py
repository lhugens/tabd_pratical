import psycopg2

conn = psycopg2.connect("dbname=leo user=leo")
cursor_psql = conn.cursor()

# get initial_point of taxi_services
sql = '''
select
st_astext(st_transform(t.initial_point, 3763))
from taxi_services t
'''
cursor_psql.execute(sql)
results = cursor_psql.fetchall()
initial_points = []

for result in results:
    print(result)
    initial_points.append(result.split("(")[1])


for initial_point in initial_points:
    print(initial_point)
