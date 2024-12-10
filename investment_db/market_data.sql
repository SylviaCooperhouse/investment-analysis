--DROP TABLE market_data
CREATE TABLE market_data (
    asset_id INT REFERENCES assets(asset_id),
    date DATE NOT NULL,
    open NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    high NUMERIC,
    low NUMERIC,
    volume BIGINT,
    PRIMARY KEY (asset_id, date)
);