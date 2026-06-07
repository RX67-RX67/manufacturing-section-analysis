-- fred_series stores Federal Reserve economic data
-- series_id: the FRED code (e.g. "IPMAN" = Industrial Production: Manufacturing)
-- UNIQUE(series_id, date): no duplicate data points per series per date
CREATE TABLE fred_series (
  id          SERIAL PRIMARY KEY,
  series_id   TEXT NOT NULL,
  date        DATE NOT NULL,
  value       NUMERIC,
  unit        TEXT,
  fetched_at  TIMESTAMPTZ DEFAULT now(),
  UNIQUE(series_id, date)
);

-- bls_series stores Bureau of Labor Statistics data
CREATE TABLE bls_series (
  id          SERIAL PRIMARY KEY,
  series_id   TEXT NOT NULL,
  date        DATE NOT NULL,
  value       NUMERIC,
  fetched_at  TIMESTAMPTZ DEFAULT now(),
  UNIQUE(series_id, date)
);

-- census_m3 stores Census Bureau manufacturing surveys
-- category: "shipments" | "orders" | "inventories"
CREATE TABLE census_m3 (
  id          SERIAL PRIMARY KEY,
  category    TEXT NOT NULL,
  industry    TEXT NOT NULL,
  date        DATE NOT NULL,
  value       NUMERIC,
  fetched_at  TIMESTAMPTZ DEFAULT now(),
  UNIQUE(category, industry, date)
);

-- bea_data stores Bureau of Economic Analysis GDP data
CREATE TABLE bea_data (
  id          SERIAL PRIMARY KEY,
  table_name  TEXT NOT NULL,
  line_desc   TEXT NOT NULL,
  date        DATE NOT NULL,
  value       NUMERIC,
  fetched_at  TIMESTAMPTZ DEFAULT now(),
  UNIQUE(table_name, line_desc, date)
);

-- ai_reports caches Claude-generated analysis text
-- data_hash: MD5 of the input data — used to skip regeneration when data hasn't changed
CREATE TABLE ai_reports (
  id            SERIAL PRIMARY KEY,
  report_key    TEXT UNIQUE NOT NULL,
  content       TEXT NOT NULL,
  data_hash     TEXT,
  model_used    TEXT,
  generated_at  TIMESTAMPTZ DEFAULT now()
);

-- etl_runs is an audit log — one row per pipeline run per source
CREATE TABLE etl_runs (
  id            SERIAL PRIMARY KEY,
  source        TEXT NOT NULL,
  status        TEXT NOT NULL,
  rows_upserted INT,
  error_msg     TEXT,
  ran_at        TIMESTAMPTZ DEFAULT now()
);