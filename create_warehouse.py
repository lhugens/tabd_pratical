import datetime
from ware_house1 import rows

for row in rows[:1]:
    print(row)

with open("./create_warehouse.sql", "w+") as out:
    # create table
    out.write('''CREATE TABLE WAREHOUSE (
id VARCHAR(2),
stop_id_start VARCHAR(10),
stop_id_end VARCHAR(10),
initial_point public.geometry(Point,3763),
final_point public.geometry(Point,3763),
stop_point_start public.geometry(Point,3763),
stop_point_end public.geometry(Point,3763),
initial_ts TIME,
final_ts TIME,
departure_time TIME,
trip_id VARCHAR(10)
);\n\n''')
    for row in rows: 
        out.write(f"insert into warehouse values {row};\n")



    

'''
(7269,  -- id
'COMB2',  -- start_stop_id
'CORD2',  -- end_stop_id
'POINT(-39305.4074267407 166258.050736514)',  -- taxi initial_point
'POINT(-40479.0179906739 163841.556681446)', -- taxi_final_point
'POINT(-39243.3306467599 166263.046807424)', -- stop_point_init
'POINT(-40574.6683797783 164096.948888512)', -- stop_point_end
1420070621, -- initial_ts
1420071792, -- final_ts
datetime.time(6, 44), -- departure_time
'703_1_B_1') -- trip_id
'''