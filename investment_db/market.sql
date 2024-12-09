CREATE TABLE markets (
    market_id SERIAL PRIMARY KEY,
    market_name VARCHAR(50) NOT NULL,
    market_type VARCHAR(20) NOT NULL
);

INSERT INTO markets (market_name, market_type) VALUES
('Crypto Market', 'crypto'),
('Stock Market', 'stock');

--select * from markets