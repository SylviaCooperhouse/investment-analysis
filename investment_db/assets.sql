CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    asset_name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
	shares INT NOT NULL
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

--this is a temp column
ALTER TABLE assets
ADD COLUMN shares INT NOT NULL DEFAULT 0;

-- Update shares for each asset in the asset table based on transactions
/*
UPDATE assets
SET shares = subquery.total_quantity
FROM (
    SELECT asset_id, 
           SUM(CASE 
                   WHEN type = 'BUY' THEN quantity 
                   WHEN type = 'SELL' THEN -quantity 
                   ELSE 0 
               END) AS total_quantity
    FROM transactions
    GROUP BY asset_id
) AS subquery
WHERE assets.asset_id = subquery.asset_id;
*/