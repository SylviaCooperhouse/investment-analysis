CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    asset_name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(50) NOT NULL
);


--DROP TABLE assets

INSERT INTO assets (asset_name, asset_type) VALUES
('Bitcoin', 'crypto'),
('Ethereum', 'crypto'),
('Dogecoin', 'crypto'),
('AAPL', 'stock'),
('GOOG', 'stock'),
('INTC', 'stock'),
('K', 'stock'),
('MSFT', 'stock'),
('PFE', 'stock');

ALTER TABLE assets
RENAME COLUMN name TO asset_name;

ALTER TABLE assets
RENAME COLUMN type TO asset_type;