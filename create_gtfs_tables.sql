/*
agency_id,agency_name,agency_url,agency_timezone,agency_lang
STCP,Sociedade Transportes Colectivos do Porto,http://www.stcp.pt,Europe/Lisbon,pt
*/

CREATE EXTENSION postgis;

CREATE TABLE AGENCY
(
agency_id VARCHAR(10),
agency_name VARCHAR(50),
agency_url VARCHAR(100),
agency_timezone VARCHAR(50),
agency_lang VARCHAR(2)
);

/*
service_id,date,exception_type
UTEISAGOST,20220815,2
...
*/

CREATE TABLE CALENDAR_DATES
(
service_id VARCHAR(10),
date DATE,
exception_type VARCHAR(10)
);

/*
service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
UTEIS,1,1,1,1,1,0,0,20220910,20221231
...
*/

CREATE TABLE CALENDAR
(
service_id VARCHAR(10),
monday NUMERIC(1),
tuesday NUMERIC(1),
wednesday NUMERIC(1),
thursday NUMERIC(1),
friday NUMERIC(1),
saturday NUMERIC(1), 
sunday NUMERIC(1),
start_date DATE, 
end_date DATE
);

/*
route_id,route_short_name,route_long_name,route_desc,route_type,route_url,route_color,route_text_color
200,200,Bolhão - Cast. Queijo,,3,http://www.stcp.pt/pt/viajar/linhas/?linha=200,187EC2,FFFFFF
...
*/

CREATE TABLE ROUTES
(
route_id VARCHAR(3),
route_short_name VARCHAR(10),
route_long_name VARCHAR(100),
route_desc VARCHAR(100),
route_type VARCHAR(10),
route_url VARCHAR(100),
route_color VARCHAR(8),
route_text_color VARCHAR(8)
);

/*
shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence
305_1_1_shp,41.144842,-8.616875,215
...
*/

CREATE TABLE SHAPES
(
shape_id VARCHAR(15),
shape_pt_lat NUMERIC,
shape_pt_lon NUMERIC,
shape_pt_sequence INTEGER
);

/*
stop_id,stop_code,stop_name,stop_lat,stop_lon,zone_id,stop_url
4CAM4,4CAM4,4 CAMINHOS,41.2060833350949,-8.52883330308102,MAI4,http://www.stcp.pt/pt/viajar/paragens/?t=detalhe&paragem=4CAM4
...
*/

CREATE TABLE STOPS
(
stop_id VARCHAR(10),
stop_code VARCHAR(10),
stop_name VARCHAR(100),
stop_lat NUMERIC(10,8),
stop_lon NUMERIC(11,8),
zone_id VARCHAR(5),
stop_url VARCHAR(100)
);

/*
trip_id,arrival_time,departure_time,stop_id,stop_sequence,stop_headsign
106_1_A_1,7:00:00,7:00:00,FRC,1,
...
*/

CREATE TABLE STOP_TIMES
(
trip_id VARCHAR(15),
arrival_time TIME,
departure_time TIME,
stop_id VARCHAR(10),
stop_sequence INTEGER,
stop_headsign VARCHAR(100)
);

/*
from_stop_id,to_stop_id,transfer_type
INF1,CAVE4,3
...
*/

CREATE TABLE TRANSFERS
(
from_stop_id VARCHAR(10),
to_stop_id VARCHAR(10),
transfer_type INTEGER
);

/*
route_id,direction_id,service_id,trip_id,trip_headsign,wheelchair_accessible,block_id,shape_id
107,1,DOMVERAO,107_1_Y_26,Estádio do Dragão,1,,107_1_1_shp
...
*/

CREATE TABLE TRIPS
(
route_id VARCHAR(10),
direction_id NUMERIC(2),
service_id VARCHAR(10),
trip_id VARCHAR(15),
trip_headsign VARCHAR(50),
wheelchair_accessible BOOLEAN,
block_id VARCHAR(10),
shape_id VARCHAR(20)
);


