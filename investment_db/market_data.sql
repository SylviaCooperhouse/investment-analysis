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

-- Add an index for fast filtering by asset_id and date
CREATE INDEX idx_market_data_asset_date
ON market_data (asset_id, date);

-- Add an index on date if you frequently query by date alone
CREATE INDEX idx_market_data_date
ON market_data (date);