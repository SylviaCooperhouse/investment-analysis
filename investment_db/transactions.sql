CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    asset_id INT REFERENCES assets(asset_id),
    date DATE NOT NULL,
    type VARCHAR(50) NOT NULL, -- buy or sell
    quantity NUMERIC NOT NULL,
    price NUMERIC NOT NULL
);