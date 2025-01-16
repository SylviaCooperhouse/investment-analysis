import sys
print(sys.executable)
print(sys.path)
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Fetch environment variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# Create SQLAlchemy engine
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Fetch data for the dashboard
def fetch_data():
    # Portfolio overview data
    portfolio_query = """
        SELECT a.asset_type, SUM(a.shares * md.close) AS total_value
        FROM assets a
        JOIN market_data md ON a.asset_id = md.asset_id
        WHERE md.date = (SELECT MAX(date) FROM market_data)
        GROUP BY a.asset_type
    """
    portfolio_data = pd.read_sql(portfolio_query, engine)
    
    # VaR data from portfolio_risk
    var_query = """
        SELECT date, historical_var, parametric_var, monte_carlo_var, type, asset_type
        FROM portfolio_risk
        ORDER BY date DESC
        LIMIT 30
    """
    var_data = pd.read_sql(var_query, engine)
    
    return portfolio_data, var_data

# Initialize Dash app
app = dash.Dash(__name__)

# Fetch initial data
portfolio_data, var_data = fetch_data()

# Layout
app.layout = html.Div([
    html.H1("Portfolio Risk Dashboard", style={'textAlign': 'center'}),

    # Portfolio Overview
    html.Div([
        html.H2("Portfolio Overview"),
        dcc.Graph(
            id="portfolio-allocation",
            figure=px.pie(
                portfolio_data, 
                names="asset_type", 
                values="total_value",
                title="Portfolio Allocation by Asset Type"
            )
        ),
    ]),

    # VaR Metrics
    html.Div([
        html.H2("Risk Metrics"),
        dcc.Graph(
            id="var-trend",
            figure=px.line(
                var_data, 
                x="date", 
                y=["historical_var", "parametric_var", "monte_carlo_var"],
                color="asset_type",
                title="VaR Trend (Last 30 Days)"
            )
        ),
    ]),

    # Historical Performance (Placeholder for future data)
    html.Div([
        html.H2("Historical Performance"),
        dcc.Graph(
            id="portfolio-performance",
            figure={  # Add more historical data here for the figure in the future
                "data": [],
                "layout": {
                    "title": "Portfolio Historical Performance (Coming Soon)"
                }
            }
        )
    ]),
])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
