import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# Connect to the database
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT
)

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
    portfolio_data = pd.read_sql(portfolio_query, conn)
    
    # VaR data
    var_query = "SELECT * FROM daily_var ORDER BY date DESC LIMIT 30"
    var_data = pd.read_sql(var_query, conn)
    
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
            figure=px.pie(portfolio_data, names="asset_type", values="total_value",
                          title="Portfolio Allocation by Asset Type")
        ),
    ]),
    
    # VaR Metrics
    html.Div([
        html.H2("Risk Metrics"),
        dcc.Graph(
            id="var-trend",
            figure=px.line(var_data, x="date", y=["historical_var", "parametric_var", "monte_carlo_var"],
                           title="VaR Trend (Last 30 Days)")
        ),
    ]),
    
    # Historical Performance
    html.Div([
        html.H2("Historical Performance"),
        dcc.Graph(
            id="portfolio-performance",
            # Add more historical data here for the figure
        )
    ]),
])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)