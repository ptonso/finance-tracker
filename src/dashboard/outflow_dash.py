import pandas as pd
from typing import *
from bokeh.models import (
    ColumnDataSource, Select, Toggle, Button, Div, TabPanel, HoverTool, FactorRange
)
from bokeh.layouts import column, row
from bokeh.plotting import figure
from bokeh.palettes import Category20
from bokeh.io import curdoc
from datetime import datetime

from src.dashboard.base_dashboard import BaseDashboard


class DimensionHandler:
    """Handles dimension-specific properties and operations for dashboard filtering."""
    
    def __init__(self, name: str, values: List[str], data_column: str):
        self.name = name
        self.values = values
        self.data_column = data_column
        self.colors = self._generate_color_mapping()
        self.toggle_buttons: Dict[str, Any] = {}
        
    def _generate_color_mapping(self) -> Dict[str, str]:
        """Creates a color mapping for dimension values using Bokeh's Category20 palette."""
        num_items = len(self.values)
        palette = Category20[20]
        extended_palette = (palette * (num_items // 20 + 1))[:num_items]
        return dict(zip(self.values, extended_palette))

    def create_toggle_buttons(self) -> Dict[str, Any]:
        """Creates toggle buttons with color indicators for each dimension value."""
        self.toggle_buttons = {
            item: row(
                Div(text=f'''
                    <div style="width: 15px; 
                                height: 15px;
                                background-color: {self.colors[item]};
                                display: inline-block; 
                                margin-right: 8px;">
                    </div>
                '''),
                Toggle(label=item, active=True, button_type="default"),
                sizing_mode="stretch_width"
            )
            for item in self.values
        }
        return self.toggle_buttons
    
    def get_colors_for_items(self, items: List[str]) -> List[str]:
        """Returns colors for the given dimension values."""
        return [self.colors[item] for item in items]


class OutflowDash(BaseDashboard):
    """Dashboard for analyzing outflow/expenditure data across time and dimensions."""
    
    title = "Outflow Analysis"
    
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
    
    def setup(self) -> None:
        """Initialize the dashboard components and data."""
        self._prepare_data()
        self._initialize_dimensions()
        self._precompute_participant_stats()
        self._setup_controls()
        self._setup_plot()
        self._setup_layout()
        self._setup_events()
        self.update_data(None, None, None)
    
    def _prepare_data(self) -> None:
        """Prepare the data for analysis by adding required columns."""
        self.data['month'] = self.data['date'].dt.strftime('%Y-%m')
        
    
    def _initialize_dimensions(self) -> None:
        """Set up dimension handlers for different grouping options."""
        category_totals = self._get_sorted_dimension_values('category')
        bank_totals = self._get_sorted_dimension_values('bank')

        self.dimensions = {
            'category': DimensionHandler('category', category_totals, 'category'),
            'bank': DimensionHandler('bank', bank_totals, 'bank')
        }
        self.current_dimension = 'category'
    
    def _get_sorted_dimension_values(self, dim_name: str) -> List[str]:
        """Get dimension values sorted by total outcome amount."""
        return (
            self.data.groupby(dim_name)['outcome']
            .sum()
            .sort_values(ascending=False)
            .index.tolist()
        )
    
    def _precompute_participant_stats(self) -> None:
        """
        Build dataframe with participant statistics for each dimension and month.
        Creates columns: [participant, <dimension>, month, monthly_outcome, avg_outcome, total_outcome]
        for tooltip display.
        """
        dfs = []
        for dim in ['category', 'bank']:
            # Calculate monthly outcomes
            temp = (
                self.data
                .groupby(['participant', dim, 'month'])['outcome']
                .sum()
                .reset_index(name='monthly_outcome')
            )

            # Calculate averages and totals
            global_stats = (
                temp.groupby(['participant', dim])['monthly_outcome']
                .agg(['mean', 'sum'])
                .reset_index()
            )

            global_stats.columns = ['participant', dim, 'avg_outcome', 'total_outcome']
            merged = pd.merge(temp, global_stats, on=['participant', dim], how='left')
            merged['dimension'] = dim
            dfs.append(merged)

        self.participant_stats = pd.concat(dfs, ignore_index=True)

    def _setup_controls(self) -> None:
        """Create and configure UI control elements."""
        # Set default date range (last 12 months to current)
        today = datetime.today()
        default_final_month = today.strftime('%Y-%m')
        default_initial_month = (today - pd.DateOffset(months=12)).strftime('%Y-%m')
        
        self.months = sorted(self.data['month'].unique().tolist())
        
        # Create selection controls
        self.start_month = Select(
            title="Start Month", 
            value=self.months[0] if self.months else default_initial_month,
            options=self.months
        )
        self.end_month = Select(
            title="End Month", 
            value=default_final_month, 
            options=self.months
        )
        self.dimension_select = Select(
            title="Group By", 
            value="category", 
            options=list(self.dimensions.keys())
        )
        
        # Create toggle buttons for the initial dimension
        self.toggle_buttons = self.dimensions['category'].create_toggle_buttons()
        
        # Add select/deselect buttons
        self.select_all_button = Button(label="Select All", button_type="success")
        self.deselect_all_button = Button(label="Deselect All", button_type="danger")
    
    def _setup_plot(self) -> None:
        """Initialize the main plot and data source."""
        self.source = ColumnDataSource(data=dict(month=[]))
        self.plot = figure(
            x_range=FactorRange(), 
            height=400, 
            width=800, 
            title="Expenditure Analysis", 
            toolbar_location=None, 
            tools=""
        )
        self.plot.xgrid.grid_line_color = None
        self.renderers = []
    
    def _setup_layout(self) -> None:
        """Arrange UI components in the final layout."""
        self.toggle_column = column(*self.toggle_buttons.values(), width=200)
        control_layout = column(
            self.dimension_select, 
            self.start_month, 
            self.end_month, 
            self.select_all_button, 
            self.deselect_all_button
        )
        self.layout = row(control_layout, self.toggle_column, self.plot)
    
    def _setup_events(self) -> None:
        """Set up event handlers for interactive controls."""
        self.suppress_update = False
        self.start_month.on_change("value", self.update_data)
        self.end_month.on_change("value", self.update_data)
        self.dimension_select.on_change("value", self._handle_dimension_change)
        
        # Add toggle event handlers
        for toggle_row in self.toggle_buttons.values():
            toggle_widget = toggle_row.children[1]
            toggle_widget.on_change("active", self.update_data)
            
        self.select_all_button.on_click(self.select_all)
        self.deselect_all_button.on_click(self.deselect_all)
    
    def _handle_dimension_change(self, attr: str, old: str, new: str) -> None:
        """Handle changes to the dimension selection dropdown."""
        self.current_dimension = new
        self.toggle_buttons = self.dimensions[new].create_toggle_buttons()
        self.toggle_column.children = list(self.toggle_buttons.values())
        self.update_data(None, None, None)
    
    def update_data(self, attr: Optional[str], old: Any, new: Any) -> None:
        """
        Update chart data based on current selections.
        This is called when any control value changes.
        """
        if self.suppress_update:
            return
        
        # Get current selections
        dim_handler = self.dimensions[self.current_dimension]
        start = self.start_month.value
        end = self.end_month.value
        
        # Reset plot
        self.plot.renderers = []
        self.renderers = []
        self.source.data = {}
        
        # Get active dimension items
        active_items = self._get_active_items()
        if not active_items:
            self.plot.x_range.factors = []
            return
        
        # Filter data based on selections
        filtered_data = self._filter_data(start, end, dim_handler.data_column, active_items)
        if filtered_data.empty:
            self.plot.x_range.factors = []
            return

        # Group data for stacked bars
        grouped_data = self._group_data(filtered_data, dim_handler.data_column)
        stackers = [col for col in grouped_data.columns if col in active_items]
        if not stackers:
            self.plot.x_range.factors = []
            return
        
        # Prepare data for plot
        data_dict = self._prepare_plot_data(grouped_data, stackers)
        self.source.data = data_dict

        # Create stacked bars with tooltips
        self._create_stacked_bars(stackers, dim_handler)

    def _get_active_items(self) -> List[str]:
        """Get list of currently active dimension items from toggle buttons."""
        return [
            item for item, toggle_row in self.toggle_buttons.items()
            if toggle_row.children[1].active
        ]
    
    def _filter_data(self, start: str, end: str, dim_column: str, active_items: List[str]) -> pd.DataFrame:
        """Filter data based on date range and active dimension items."""
        return self.data[
            (self.data['month'] >= start) &
            (self.data['month'] <= end) &
            (self.data[dim_column].isin(active_items))
        ].copy()
    
    def _group_data(self, data: pd.DataFrame, dim_column: str) -> pd.DataFrame:
        """Group data by month and dimension for stacked bar chart."""
        grouped = (
            data
            .groupby(['month', dim_column])['outcome']
            .sum()
            .unstack(fill_value=0)
        )
        return grouped.reset_index()
    
    def _prepare_plot_data(self, grouped: pd.DataFrame, stackers: List[str]) -> Dict[str, List[Any]]:
        """Prepare data dictionary for ColumnDataSource with tooltips."""
        # Set x-axis categories
        months = grouped['month'].tolist()
        factors = [tuple(m.split('-')) for m in months]  
        self.plot.x_range.factors = factors
        
        # Create tooltip lookup from participant stats
        tooltip_lookup = self._create_tooltip_lookup()
        
        # Build data dictionary with values and tooltips
        data_dict = {'month_factors': factors}
        for stacker in stackers:
            data_dict[stacker] = grouped[stacker].tolist()
            data_dict[f"{stacker}_tooltip"] = self._generate_tooltips(grouped, stacker, tooltip_lookup)
            
        return data_dict
    
    def _create_tooltip_lookup(self) -> Dict[str, Dict[str, Tuple[float, float, float]]]:
        """Create lookup dictionary for tooltip data."""
        stats_df = self.participant_stats[
            self.participant_stats['dimension'] == self.current_dimension
        ].copy()
        stats_df['key'] = stats_df['month'] + "||" + stats_df[self.current_dimension].astype(str)

        lookup = {}
        for row in stats_df.itertuples():
            key = row.key
            if key not in lookup:
                lookup[key] = {}
            lookup[key][row.participant] = (
                row.monthly_outcome,
                row.avg_outcome,
                row.total_outcome
            )
        return lookup
    
    def _generate_tooltips(self, grouped: pd.DataFrame, stacker: str, 
                          lookup: Dict[str, Dict[str, Tuple[float, float, float]]]) -> List[str]:
        """Generate HTML tooltip content for each data point."""
        tooltip_col = []
        for _, grow in grouped.iterrows():
            month = grow['month']
            key = month + "||" + str(stacker)

            if key not in lookup:
                tooltip_col.append("No data")
                continue

            # Get participant data for this month and dimension value
            participant_data = []
            for participant, (monthly, avg, total) in lookup[key].items():
                participant_data.append((participant, monthly, avg, total))

            # Sort by monthly outcome and take top 15
            participant_data.sort(key=lambda x: x[1], reverse=True)
            participant_data = participant_data[:15]
            
            # Generate HTML table
            tooltip_col.append(self._generate_tooltip_table(stacker, participant_data))
            
        return tooltip_col
    
    def _truncate_text(self, text: str, max_length: int = 10) -> str:
        """Truncate text and add ellipsis if longer than max_length."""
        if len(text) <= max_length:
            return text
        return text[:max_length-1] + "…"
    
    def _generate_tooltip_table(self, category_name: str, participant_data: List[Tuple[str, float, float, float]]) -> str:
        """Generate styled HTML table for tooltip display with consistent column widths and truncated names."""
        # CSS styles for the table
        rows = []
        for index, (participant, monthly, avg, total) in enumerate(participant_data):
            truncated_name = self._truncate_text(participant, 30)
            row_color = "#f8f8f8" if index & 2 == 0 else '#ffffff'

            rows.append(
                f"<tr style='background-color: {row_color};'>"
                f"<td style='padding: 5px 8px; border-bottom: 1px solid #ddd; white-space: nowrap;' title='{participant}'>{truncated_name}</td>"
                f"<td style='padding: 5px 8px; border-bottom: 1px solid #ddd; text-align: right;'>{monthly:.2f}</td>"
                f"<td style='padding: 5px 8px; border-bottom: 1px solid #ddd; text-align: right;'>{avg:.2f}</td>"
                f"<td style='padding: 5px 8px; border-bottom: 1px solid #ddd; text-align: right;'>{total:.2f}</td>"
                f"</tr>"
            )

        table_html = (
            f"<div style='font-weight: bold; text-align: center; padding: 4px 0; font-size: 12px;'>"
            f"{category_name}</div>"
            "<table style='border-collapse: collapse; width: 100%; max-width: 280px; font-size: 11px; box-shadow: 0 2px 4px rgba(0,0,0,0.15); border-radius: 4px;'>"
            "<thead>"
            "<tr style='background-color: #f2f2f2; color: #333; font-weight: bold; text-align: left;'>"
            "<th style='padding: 6px 8px; border-bottom: 1px solid #ddd; white-space: nowrap;'>Participant</th>"
            "<th style='padding: 6px 8px; border-bottom: 1px solid #ddd; text-align: right;'>Month</th>"
            "<th style='padding: 6px 8px; border-bottom: 1px solid #ddd; text-align: right;'>Avg</th>"
            "<th style='padding: 6px 8px; border-bottom: 1px solid #ddd; text-align: right;'>Total</th>"
            "</tr>"
            "</thead>"
            "<tbody>"
            + "".join(rows) +
            "</tbody>"
            "</table>"
    )

        return table_html
    
    def _create_stacked_bars(self, stackers: List[str], dim_handler: DimensionHandler) -> None:
        """Create stacked bar renderers with hover tooltips."""
        colors = dim_handler.get_colors_for_items(stackers)
        self.renderers = self.plot.vbar_stack(
            stackers=stackers,
            x='month_factors',
            width=0.8,
            source=self.source,
            color=colors,
            name=stackers
        )
        
        # Add hover tool for each stacked bar segment
        for i, renderer in enumerate(self.renderers):
            stacker = stackers[i]
            hover_tool = HoverTool(
                renderers=[renderer],
                tooltips=[("", f"@{{{stacker}_tooltip}}{{safe}}")]
            )
            self.plot.add_tools(hover_tool)

    def select_all(self) -> None:
        """Select all dimension toggle buttons."""
        self.suppress_update = True
        for toggle_row in self.toggle_buttons.values():
            toggle_widget = toggle_row.children[1]
            toggle_widget.active = True
        self.suppress_update = False
        self.update_data(None, None, None)
    
    def deselect_all(self) -> None:
        """Deselect all dimension toggle buttons."""
        self.suppress_update = True
        for toggle_row in self.toggle_buttons.values():
            toggle_widget = toggle_row.children[1]
            toggle_widget.active = False
        self.suppress_update = False
        self.update_data(None, None, None)
    
    def create_tab_panel(self) -> TabPanel:
        """Create a tab panel containing this dashboard."""
        return TabPanel(child=self.layout, title=self.title)
    
    @classmethod
    def init_standalone(cls) -> Optional['OutflowDash']:
        """Initialize dashboard for standalone mode."""
        try:
            from src.utils.load_data import load_dashboard_data
            data = load_dashboard_data()['nubank']
            if data is None:
                return None
            dashboard = cls(data)
            doc = curdoc()
            doc.add_root(dashboard.layout)
            doc.title = cls.title
            return dashboard
        except Exception as e:
            print(f"Error in standalone initialization: {str(e)}")
            raise


# For standalone testing
# OutflowDash.init_standalone()
# python3 -m dotenv run bokeh serve src/dashboard/outflow_dash.py --show