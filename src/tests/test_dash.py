from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, curdoc
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from src.tests.toy_dataset import generate_transactions


def generate_transactions(start_date):
    """Generate sample transaction data."""
    dates = [start_date + timedelta(days=x) for x in range(100)]
    amounts = np.random.normal(1000, 200, 100)
    categories = np.random.choice(['A', 'B', 'C'], 100)
    
    return pd.DataFrame({
        'date': dates,
        'amount': amounts,
        'category': categories
    })

def create_dashboard():
    """Create and initialize the dashboard"""
    print("Starting dashboard creation...")
    
    # Load data
    start_date = datetime(2023, 1, 1)
    data = generate_transactions(start_date)
    print("Loaded data:", data.head())
    print("Data columns:", data.columns.tolist())
    
    # Create the data source
    source = ColumnDataSource(data)
    
    # Create the main scatter plot
    fig = figure(
        title="Outflow Analysis",
        width=800,
        height=400,
        tools="pan,box_zoom,reset,save",
        x_axis_label='Date',
        y_axis_label='Amount'
    )
    
    # Add scatter points
    fig.circle(
        x='date',
        y='amount',
        size=8,
        alpha=0.6,
        source=source
    )
    
    layout = column(fig)
    print("Dashboard creation completed!")
    return layout

# This is the main entry point for Bokeh
def main():
    layout = create_dashboard()
    # Add the layout to the current document
    doc = curdoc()
    doc.add_root(layout)
    doc.title = "Test Dashboard"

# When running with bokeh serve, this will be called
main()