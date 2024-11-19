from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Select, Toggle, Button, Div
from bokeh.layouts import column, row
from bokeh.plotting import figure
from bokeh.palettes import Category20
import pandas as pd
from datetime import datetime

# Example dataset
from toy_dataset import generate_transactions
start_date = datetime(2023, 1, 1)
df = generate_transactions(start_date)

from frame_csv import frame_dir
reconciled_dir = "data/03_reconciled"
df = frame_dir(reconciled_dir)

class CategoryDashboard:
    def __init__(self, data):
        self.data = data
        self.categories = sorted(data['category'].unique())
        self.data['month'] = self.data['date'].dt.to_period('M').dt.strftime('%Y-%m')
        self.months = sorted(self.data['month'].unique())

        # Dropdowns for initial and final months
        today = datetime.today()
        default_final_month = today.strftime('%Y-%m')
        default_initial_month = (today - pd.DateOffset(months=12)).strftime('%Y-%m')

        self.start_month = Select(title="Start Month", value=default_initial_month, options=self.months)
        self.end_month = Select(title="End Month", value=default_final_month, options=self.months)

        # Data source for the bar chart
        self.source = ColumnDataSource(data=dict(month=[]))

        # Color map
        num_categories = len(self.categories)
        colors = Category20[20][:num_categories] if num_categories <= 20 else Category20[20] * ((num_categories // 20) + 1)
        self.color_map = dict(zip(self.categories, colors))

        # Category Toggles with Colored Boxes
        self.category_toggles = {
            cat: row(
                Div(text=f'<div style="width: 15px; height: 15px; background-color: {self.color_map[cat]}; display: inline-block; margin-right: 8px;"></div>'),
                Toggle(label=cat, active=True, button_type="default"),
                sizing_mode="stretch_width"
            )
            for cat in self.categories
        }

        self.select_all_button = Button(label="Select All", button_type="success")
        self.deselect_all_button = Button(label="Deselect All", button_type="danger")

        # Stacked bar chart
        self.plot = figure(
            x_range=[], height=400, width=800, title="Category Expenditures",
            toolbar_location=None, tools=""
        )
        self.plot.xgrid.grid_line_color = None

        self.renderers = []
        self.suppress_update = False

        # Layout
        toggle_layout = column(*self.category_toggles.values(), width=200)
        control_layout = column(self.start_month, self.end_month, self.select_all_button, self.deselect_all_button)
        self.layout = row(control_layout, toggle_layout, self.plot)

        # Event listeners
        self.start_month.on_change("value", self.update_data)
        self.end_month.on_change("value", self.update_data)
        for toggle_row in self.category_toggles.values():
            toggle_widget = toggle_row.children[1]  # Access the Toggle inside the row
            toggle_widget.on_change("active", self.update_data)
        self.select_all_button.on_click(self.select_all)
        self.deselect_all_button.on_click(self.deselect_all)

        # Initial data update
        self.update_data(None, None, None)

    def update_data(self, attr, old, new):
        if self.suppress_update:
            return

        # Filter data by date range
        start = self.start_month.value
        end = self.end_month.value
        mask = (self.data['month'] >= start) & (self.data['month'] <= end)
        filtered = self.data[mask]

        # Filter by active categories
        active_categories = [
            cat for cat, toggle_row in self.category_toggles.items() if toggle_row.children[1].active
        ]
        filtered = filtered[filtered['category'].isin(active_categories)]

        # Remove existing renderers
        for r in self.renderers:
            self.plot.renderers.remove(r)
        self.renderers = []

        if not filtered.empty and active_categories:
            # Aggregate data for stacked bar chart
            grouped = filtered.groupby(['month', 'category'])['outcome'].sum().unstack(fill_value=0)
            grouped = grouped.reset_index().set_index('month')
            grouped = grouped.reindex(columns=active_categories, fill_value=0).reset_index()

            # Update the ColumnDataSource
            self.source.data = {col: grouped[col].tolist() for col in grouped.columns}
            self.plot.x_range.factors = grouped['month'].tolist()

            # Get colors for active categories
            active_colors = [self.color_map[cat] for cat in active_categories]

            # Create new vbar_stack
            self.renderers = self.plot.vbar_stack(
                stackers=active_categories, x="month", width=0.8, source=self.source,
                color=active_colors
            )
        else:
            self.source.data = {'month': []}
            self.plot.x_range.factors = []

    def select_all(self):
        self.suppress_update = True
        for toggle_row in self.category_toggles.values():
            toggle_widget = toggle_row.children[1]  # Access the Toggle inside the row
            toggle_widget.active = True
        self.suppress_update = False
        self.update_data(None, None, None)

    def deselect_all(self):
        self.suppress_update = True
        for toggle_row in self.category_toggles.values():
            toggle_widget = toggle_row.children[1]  # Access the Toggle inside the row
            toggle_widget.active = False
        self.suppress_update = False
        self.update_data(None, None, None)

    def run(self, doc):
        doc.add_root(self.layout)

# Run the dashboard
dashboard = CategoryDashboard(df)
dashboard.run(curdoc())
