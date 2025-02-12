SELECT * FROM market_data LIMIT 100
SELECT * FROM markets
SELECT * FROM assets
SELECT * FROM transactions


WITH market_data_check AS(
SELECT DISTINCT asset_id FROM market_data
)
SELECT * FROM assets ast
LEFT JOIN market_data_check mdc ON mdc.asset_id = ast.asset_id


UPDATE table_name
SET column1 = value1, column2 = value2, ...
WHERE condition;