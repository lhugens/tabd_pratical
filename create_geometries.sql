-- enable PostGis extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- add a new columnn to stops table for storing stop coordinates in Point geometry, SRID 3763
ALTER TABLE stops ADD COLUMN point geometry(Point, 3763);

-- load the created column with stop_lon and stop_lat coorinates
UPDATE stops SET geom = ST_SetSRID(ST_MakePoint(stop_lon, stop_lat), 3763);

