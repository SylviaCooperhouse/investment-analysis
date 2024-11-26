CREATE TABLE market_data (
    market_id SERIAL PRIMARY KEY,
    asset_id INT REFERENCES assets(asset_id),
    date DATE NOT NULL,
    open NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    high NUMERIC,
    low NUMERIC,
    volume BIGINT
);