SELECT * FROM assets
SELECT * FROM market_data WHERE asset_id = 4 ORDER BY 2 DESC


        SELECT md.date,a.asset_type, SUM(a.shares * md.close) AS total_value
        FROM assets a
        JOIN market_data md ON a.asset_id = md.asset_id
        WHERE md.date = (SELECT MAX(date) FROM market_data)
        GROUP BY md.date,a.asset_type