CREATE TYPE PARAMETER as (
  name TEXT,
  units TEXT ,
  value NUMERIC,
  max_allowed_concentration NUMERIC
);

CREATE TYPE WATER_PARAMETERS as (
  smell PARAMETER,
  taste PARAMETER ,
  color PARAMETER,
  muddiness PARAMETER,
  general_mineralization PARAMETER
);

CREATE TABLE IF NOT EXISTS HEXAGONS ( 
  hex_id TEXT NOT NULL,
  created_at timestamp NOT NULL,
  hex_color TEXT NOT NULL,
  water_parameters WATER_PARAMETERS NOT NULL
);

INSERT INTO HEXAGONS VALUES (
  '891fb466257ffff',
  NOW(),
  '#e24d2d', 
  ROW(
    ROW('Smell', 'units', 1.5, 2.0),       -- smell
    ROW('Taste', 'units', 1.2, 2.0),       -- taste
    ROW('Color', 'units', 0.8, 1.5),       -- color
    ROW('Muddiness', 'units', 0.5, 1.0),   -- muddiness
    ROW('General Mineralization', 'units', 150, 200)  -- general_mineralization
  )::WATER_PARAMETERS
);
