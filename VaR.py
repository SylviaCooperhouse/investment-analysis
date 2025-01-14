# Store VaR results in the database
date_today = datetime.now().date()
try:
    cursor.execute("""
        INSERT INTO portfolio_risk (date, historical_var, parametric_var, monte_carlo_var, type)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (date, type) DO UPDATE SET
            historical_var = EXCLUDED.historical_var,
            parametric_var = EXCLUDED.parametric_var,
            monte_carlo_var = EXCLUDED.monte_carlo_var;
    """, (
        date_today,
        float(crypto_var[0]),  # Convert np.float64 to Python float
        float(crypto_var[1]),
        float(crypto_var[2]),
        'crypto'
    ))
    cursor.execute("""
        INSERT INTO portfolio_risk (date, historical_var, parametric_var, monte_carlo_var, type)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (date, type) DO UPDATE SET
            historical_var = EXCLUDED.historical_var,
            parametric_var = EXCLUDED.parametric_var,
            monte_carlo_var = EXCLUDED.monte_carlo_var;
    """, (
        date_today,
        float(stock_var[0]),  # Convert np.float64 to Python float
        float(stock_var[1]),
        float(stock_var[2]),
        'stocks'
    ))
    cursor.execute("""
        INSERT INTO portfolio_risk (date, historical_var, parametric_var, monte_carlo_var, type)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (date, type) DO UPDATE SET
            historical_var = EXCLUDED.historical_var,
            parametric_var = EXCLUDED.parametric_var,
            monte_carlo_var = EXCLUDED.monte_carlo_var;
    """, (
        date_today,
        float(portfolio_var[0]),  # Convert np.float64 to Python float
        float(portfolio_var[1]),
        float(portfolio_var[2]),
        'portfolio'
    ))
    conn.commit()
    print("VaR results successfully stored in the database.")
except Exception as e:
    conn.rollback()
    print(f"Error storing VaR results: {e}")
