"""
Main application script for running all dashboards in a tabbed interface
"""
from bokeh.models import Tabs
from bokeh.io import curdoc
import pandas as pd
from datetime import datetime

# Import dashboard classes
from src.dashboard.outflow_dash import OutflowDash
from src.dashboard.cashflow_dash import CashFlowDash

# from src.dashboard.spending_heatmap import SpendingHeatmap
# from src.dashboard.outlier_detection import OutlierDetection
# from src.dashboard.planner_dash import PlannerDash
# from src.dashboard.scenario_dash import ScenarioDash

from src.utils.config import load_config
from src.utils.load_data import load_dashboard_data

def create_dashboard_app(data):
    """
    Create the main dashboard application with all tabs
    
    Args:
        data (pd.DataFrame): Transaction data
    
    Returns:
        bokeh.models.Tabs: Tabbed interface with all dashboards
    """
    # Initialize dashboards
    dashboard_panels = []

    dashboards = [
        OutflowDash,
        CashFlowDash,
    ]

    for dashboard_class in dashboards:
        try:
            dash = dashboard_class(data)
            panel = dash.create_tab_panel()
            dashboard_panels.append(panel)
        except Exception as e:
            print(f"Error initializing {dashboard_class.__name__}: {e}")
        
    if dashboard_panels:
        tabs = Tabs(tabs=dashboard_panels)
        return tabs
    else:
        from bokeh.layouts import column
        from bokeh.models import Div
        error_msg = Div(text="<h2>Error: No dashboards could be initialized</h2>")
        return column(error_msg)

def main():
    """Main entry point for the dashboard application"""
    # Load data
    USE_TOY_DATA: bool = False

    if USE_TOY_DATA:
        from src.tests.toy_dataset import generate_transactions
        data = generate_transactions(start_date=datetime(2023, 1, 1))
    else:
        data = load_dashboard_data()["nubank"]
    
    # Create dashboard
    dashboard = create_dashboard_app(data)
    
    # Add to document
    curdoc().add_root(dashboard)
    
    # Add title
    curdoc().title = "Financial Analytics Dashboard"

main()

# Run with:
# python3 -m dotenv run bokeh serve run_dashboards.py --show