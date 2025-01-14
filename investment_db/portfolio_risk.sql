CREATE TABLE portfolio_risk (
    date DATE PRIMARY KEY,
	
    historical_var NUMERIC,
    parametric_var NUMERIC,
    monte_carlo_var NUMERIC
);

SELECT * FROM portfolio_risk
--DROP TABLE portfolio_risk


-- Step 1: Add a new column 'type' to the table
ALTER TABLE portfolio_risk
ADD COLUMN type CHARACTER VARYING;
ALTER TABLE portfolio_risk
ADD COLUMN asset_type CHARACTER VARYING;
-- Step 2: Update the existing rows to set the 'type' column to 'portfolio'
UPDATE portfolio_risk
SET asset_type = 'portfolio'
WHERE asset_type IS NULL;

UPDATE portfolio_risk
SET type = 'rate of return'
WHERE type IS NULL;

-- Verify the update
SELECT * FROM portfolio_risk;