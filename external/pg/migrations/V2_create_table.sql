CREATE TYPE PARAMETER as (
  name TEXT,
  units TEXT ,
  value NUMERIC,
  max_allowed_concentration NUMERIC
);

CREATE TYPE WATER_PARAMETERS as (
  smell PARAMETER,
  taste PARAMETER,
  color PARAMETER,
  muddiness PARAMETER,
  general_mineralization PARAMETER
);

CREATE TYPE COLOR as (
    red SMALLINT,
    green SMALLINT,
    blue SMALLINT
);

CREATE TABLE IF NOT EXISTS HEXAGONS (
  created_at timestamp NOT NULL,
  hex_id TEXT NOT NULL,
  hex_resolution INTEGER NOT NULL,
  hex_color TEXT NOT NULL,
  avg_water_parameters WATER_PARAMETERS
);

INSERT INTO HEXAGONS VALUES (
  NOW(),
  '871fb4662ffffff',
  7, -- resolution
  ROW(
    148,
    211,
    31
  )::COLOR,
  ROW(
    ROW('Запах', 'баллы', 1.5, 2.0),       -- smell
    ROW('Привкус', 'баллы', 1.2, 2.0),       -- taste
    ROW('Цветность', 'градусы', 0.8, 1.5),       -- color
    ROW('Мутность', 'мг/дм3', 0.5, 1.0),   -- muddiness
    ROW('Общая минерализация  ***', 'мг/дм3', 150, 200)  -- general_mineralization
  )::WATER_PARAMETERS
);

CREATE TYPE GEO_POINT as (
    latitude NUMERIC,
    longitude NUMERIC
);

CREATE TABLE IF NOT EXISTS HOUSES_WATER_QUALITY (
  created_at timestamp NOT NULL,
  address TEXT NOT NULL,
  coordinates GEO_POINT NOT NULL,
  water_parameters WATER_PARAMETERS
);

INSERT INTO HOUSES_WATER_QUALITY VALUES (
  NOW(),
  'Республика Беларусь, г.Минск, Газеты Звязда просп., 42',
  ROW(
    53.86037,
    27.46016
  )::GEO_POINT,
  ROW(
    ROW('Запах', 'баллы', 1.5, 2.0),       -- smell
    ROW('Привкус', 'баллы', 1.2, 2.0),       -- taste
    ROW('Цветность', 'градусы', 0.8, 1.5),       -- color
    ROW('Мутность', 'мг/дм3', 0.5, 1.0),   -- muddiness
    ROW('Общая минерализация  ***', 'мг/дм3', 150, 200)  -- general_mineralization
  )::WATER_PARAMETERS
);