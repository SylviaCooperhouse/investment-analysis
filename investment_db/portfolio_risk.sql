CREATE TABLE portfolio_risk (
    date DATE PRIMARY KEY,
    historical_var NUMERIC,
    parametric_var NUMERIC,
    monte_carlo_var NUMERIC
);