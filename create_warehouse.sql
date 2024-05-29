CREATE TABLE WAREHOUSE (
    route_id VARCHAR(50),
    trip_id VARCHAR(50),
    stop_id_start VARCHAR(50),
    stop_id_end VARCHAR(50),
    initial_ts INTEGER,
    final_ts INTEGER,
    init_stop_time TIME,
    end_stop_time TIME,
    initial_point public.geometry(Point,3763),
    final_point public.geometry(Point,3763),
    stop_point_start public.geometry(Point,3763),
    stop_point_end public.geometry(Point,3763)
);