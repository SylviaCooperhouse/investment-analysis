-- Update shares for stocks
UPDATE assets
SET shares = 32
WHERE asset_id = 4; -- AAPL

UPDATE assets
SET shares = 1
WHERE asset_id = 5; -- GOOG

UPDATE assets
SET shares = 342
WHERE asset_id = 6; -- INTC

UPDATE assets
SET shares = 1
WHERE asset_id = 7; -- K

UPDATE assets
SET shares = 18
WHERE asset_id = 8; -- MSFT

UPDATE assets
SET shares = 109
WHERE asset_id = 9; -- PFE

-- Update shares for cryptocurrencies
UPDATE assets
SET shares = 10.033151
WHERE asset_id = 2; -- Ethereum

UPDATE assets
SET shares = 5381.173892
WHERE asset_id = 3; -- Dogecoin
