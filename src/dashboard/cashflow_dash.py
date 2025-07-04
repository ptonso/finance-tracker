from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Div, Select, TabPanel
from bokeh.layouts import column, row, layout
from bokeh.plotting import figure
from bokeh.transform import dodge
import pandas as pd
from datetime import datetime

from src.dashboard.base_dashboard import BaseDashboard

class CashFlowDash(BaseDashboard):
    """Dashboard for analyzing cash flow patterns"""
    
    title = "Cash Flow Analysis"
    
    def __init__(self, data):
        super().__init__(data)
    
    def setup(self):
        """Setup dashboard components and layout"""
        # Initialize core attributes
        self.filtered_data = None
        self.total_width = 1024

        # Process data
        self.data['month'] = self.data['date'].dt.to_period('M').dt.strftime('%Y-%m')
        self.months = sorted(self.data['month'].unique())

        # Initialize components
        self._setup_controls()
        self._setup_plots()
        self._setup_summary_divs()
        self._setup_layout()
        self._setup_events()
        
        # Initial update
        self.update_data(None, None, None)
    
    def _setup_controls(self):
        """Setup control widgets"""
        today = datetime.today()
        default_final_month = today.strftime('%Y-%m')
        default_initial_month = (today - pd.DateOffset(months=12)).strftime('%Y-%m')

        self.initial_month_select = Select(
            title="Start Month",
            value=default_initial_month,
            options=self.months
        )
        self.final_month_select = Select(
            title="Final Month",
            value=default_final_month,
            options=self.months
        )
        
        self.source = ColumnDataSource(data=dict(
            month_label=[],
            income=[],
            outcome=[],
            profit_loss=[],
            profit_loss_color=[]
        ))

    def _setup_plots(self):
        """Setup plot figures"""
        # Cash Flow Plot
        self.cash_flow = figure(
            x_range=[],
            height=200,
            width=self.total_width,
            title="Cash Flow",
            toolbar_location=None,
            tools=""
        )
        self.cash_flow.vbar(
            x=dodge('month_label', -0.2, range=self.cash_flow.x_range),
            top='income',
            width=0.4,
            source=self.source,
            color="lightgreen"
        )
        self.cash_flow.vbar(
            x=dodge('month_label', 0.2, range=self.cash_flow.x_range),
            top='outcome',
            width=0.4,
            source=self.source,
            color="lightcoral"
        )
        self.cash_flow.xgrid.grid_line_color = None

        # Legend
        self.legend_div = Div(
            text="""<div style='font-size: 13px;'>
                        <span style='color: lightgreen;'>■</span> Income &nbsp;&nbsp;
                        <span style='color: lightcoral;'>■</span> Outcome
                    </div>""",
            width=self.total_width,
            height=30,
        )

        # Profit/Loss Plot
        self.profit_loss = figure(
            x_range=[],
            height=150,
            width=self.total_width,
            title="Profit/Loss",
            toolbar_location=None,
            tools=""
        )
        self.profit_loss.vbar(
            x='month_label',
            top='profit_loss',
            source=self.source,
            width=0.4,
            color='profit_loss_color',
            bottom=0
        )
        self.profit_loss.xgrid.grid_line_color = None

    def _setup_summary_divs(self):
        """Setup summary information divs"""
        self.initial_balance_div = Div(width=self.total_width // 3)
        self.final_balance_div = Div(width=self.total_width // 3)
        self.profit_loss_div = Div(width=self.total_width // 3)

    def _setup_layout(self):
        """Setup the dashboard layout"""
        self.layout = column(
            row(self.initial_month_select, self.final_month_select),
            row(
                self.initial_balance_div,
                self.final_balance_div,
                self.profit_loss_div
            ),
            self.legend_div,
            self.cash_flow,
            self.profit_loss,
        )

    def _setup_events(self):
        """Setup event handlers"""
        self.initial_month_select.on_change('value', self.update_data)
        self.final_month_select.on_change('value', self.update_data)

    def prepare_data(self):
        """Prepare data for visualization"""
        initial_date = pd.Timestamp(self.initial_month_select.value + "-01")
        final_date = pd.Timestamp(self.final_month_select.value + "-01") + pd.offsets.MonthEnd()

        self.data = self.data.sort_values('date').reset_index(drop=True)

        # Find closest dates
        if initial_date not in self.data['date'].values:
            idx = self.data['date'].searchsorted(initial_date, side='right')
            initial_date = self.data['date'].iloc[idx] if idx < len(self.data) else self.data['date'].iloc[-1]

        if final_date not in self.data['date'].values:
            idx = self.data['date'].searchsorted(final_date, side='left') - 1
            final_date = self.data['date'].iloc[idx] if idx >= 0 else self.data['date'].iloc[0]

        self.filtered_data = self.data[
            (self.data['date'] >= initial_date) & (self.data['date'] <= final_date)
        ]

        monthly_data = self.filtered_data.groupby('month').agg(
            income=('income', 'sum'),
            outcome=('outcome', 'sum'),
            ending_balance=('balance', 'last')
        ).reset_index()
        
        monthly_data['profit_loss'] = monthly_data['income'] - monthly_data['outcome']
        monthly_data['month_label'] = pd.to_datetime(monthly_data['month']).dt.strftime('%b %Y')
        monthly_data['profit_loss_color'] = [
            'lightgreen' if x > 0 else 'lightcoral' for x in monthly_data['profit_loss']
        ]

        self.adjusted_initial_date = initial_date
        self.adjusted_final_date = final_date

        return monthly_data

    def update_data(self, attr, old, new):
        """Update dashboard data and visuals"""
        data = self.prepare_data()

        self.source.data = {
            'month_label': data['month_label'],
            'income': data['income'],
            'outcome': data['outcome'],
            'profit_loss': data['profit_loss'],
            'profit_loss_color': data['profit_loss_color']
        }
        
        self.cash_flow.x_range.factors = list(data['month_label'])
        self.profit_loss.x_range.factors = list(data['month_label'])

        if not self.filtered_data.empty:
            initial_balance = self.data.loc[self.data['date'] == self.adjusted_initial_date, 'balance'].values[0]
            final_balance = self.data.loc[self.data['date'] == self.adjusted_final_date, 'balance'].values[0]
            profit_loss_total = final_balance - initial_balance
            
            self.initial_balance_div.text = f"<h3>Initial Balance:<br>{initial_balance:,.2f}</h3>"
            self.final_balance_div.text = f"<h3>Final Balance:<br>{final_balance:,.2f}</h3>"
            self.profit_loss_div.text = f"<h3>Profit/Loss:<br>{profit_loss_total:,.2f}</h3>"

    @classmethod
    def init_standalone(cls):
        """Initialize the dashboard as a standalone application"""
        print("Starting standalone initialization...")
        
        try:
            from src.tests.toy_dataset import generate_transactions
            print("Generating test data...")
            start_date = datetime(2023, 1, 1)
            data = generate_transactions(start_date)
            
            if data is None:
                print("Error: No data generated")
                return
                
            print("Creating dashboard instance...")
            dashboard = cls(data)
            
            print("Adding dashboard to document...")
            doc = curdoc()
            doc.add_root(dashboard.layout)
            doc.title = cls.title
            
            print("Standalone initialization complete")
            return dashboard
            
        except Exception as e:
            print(f"Error in standalone initialization: {str(e)}")
            raise



# For standalone testing
# CashFlowDash.init_standalone()
# python3 -m dotenv run bokeh serve src/dashboard/cashflow_dash.py --show