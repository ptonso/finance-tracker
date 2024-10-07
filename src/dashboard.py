
import sys
import pandas as pd
import json

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import plotly.graph_objects as go
from plotly.graph_objs import Figure
import plotly.express as px


class CashFlowDashboard():
    def __init__(self, df):
        self.df = df
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['month'] = self.df['date'].dt.to_period('M')
        self.available_months = self.df['month'].astype(str).unique()
        self.available_months_asc = sorted(self.available_months)
        self.available_months_desc = sorted(self.available_months, reverse=True)
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.layout()

    def layout(self):
        self.app.layout = html.Div([
            html.H1("Cash Flow Dashboard"),
            html.Div([
                dcc.Dropdown(
                    id='start-month',
                    options=[{'label': month, 'value': month} for month in self.available_months_asc],
                    value=min(self.available_months),
                    clearable=False,
                    style={'width': '48%', 'display': 'inline-block'}
                ),
                dcc.Dropdown(
                    id='end-month',
                    options=[{'label': month, 'value': month} for month in self.available_months_desc],
                    value=max(self.available_months),
                    clearable=False,
                    style={'width': '48%', 'display': 'inline-block'}
                ),
            ], style={'padding': '10px'}),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody(html.H5(id='beginning-balance', style={'font-size': '14px', 'margin': '0'}))), width=2),
                dbc.Col(dbc.Card(dbc.CardBody(html.H5(id='cash-going-in', style={'font-size': '14px', 'margin': '0'}))), width=2),
                dbc.Col(dbc.Card(dbc.CardBody(html.H5(id='cash-going-out', style={'font-size': '14px', 'margin': '0'}))), width=2),
                dbc.Col(dbc.Card(dbc.CardBody(html.H5(id='profit-loss', style={'font-size': '14px', 'margin': '0'}))), width=2),
                dbc.Col(dbc.Card(dbc.CardBody(html.H5(id='ending-balance', style={'font-size': '14px', 'margin': '0'}))), width=2),
            ], style={'margin-bottom': '10px'}),
            dcc.Graph(id='cash-flow-chart', style={'height': '60vh'}),
            dbc.Row([
                dbc.Col(dcc.Graph(id='profit-loss-chart', style={'height': '45vh'}), width=4),
                dbc.Col(dcc.Graph(id='income-summary', style={'height': '45vh'}), width=4),
                dbc.Col(dcc.Graph(id='outcome-summary', style={'height': '45vh'}), width=4),
            ]),
        ])
        self.callbacks()

    def callbacks(self):
        @self.app.callback(
            [Output('beginning-balance', 'children'),
             Output('cash-going-in', 'children'),
             Output('cash-going-out', 'children'),
             Output('profit-loss', 'children'),
             Output('ending-balance', 'children'),
             Output('cash-flow-chart', 'figure'),
             Output('profit-loss-chart', 'figure'),
             Output('income-summary', 'figure'),
             Output('outcome-summary', 'figure')],
            [Input('start-month', 'value'),
             Input('end-month', 'value')]
        )
        def update_dashboard(start_month, end_month):
            mask = (self.df['month'].astype(str) >= start_month) & (self.df['month'].astype(str) <= end_month)
            filtered_df = self.df[mask]
            monthly_df = filtered_df.groupby('month').agg({
                'income': 'sum',
                'outcome': 'sum',
                'balance': 'last'
            }).reset_index()
            beginning_balance = filtered_df['balance'].iloc[0]
            ending_balance = filtered_df['balance'].iloc[-1]
            cash_going_in = filtered_df['income'].sum()
            cash_going_out = filtered_df['outcome'].sum()
            profit_loss = cash_going_in - cash_going_out
            cash_flow_fig = go.Figure()
            cash_flow_fig.add_trace(go.Bar(
                x=monthly_df['month'].astype(str),
                y=monthly_df['income'],
                name='Income',
                marker_color='lightgreen',
                yaxis='y2'
            ))
            cash_flow_fig.add_trace(go.Bar(
                x=monthly_df['month'].astype(str),
                y=monthly_df['outcome'],
                name='Outcome',
                marker_color='lightcoral',
                yaxis='y2'
            ))
            cash_flow_fig.add_trace(go.Scatter(
                x=monthly_df['month'].astype(str),
                y=monthly_df['balance'],
                name='Ending Balance',
                mode='lines+markers',
                marker_color='grey'
            ))
            cash_flow_fig.update_layout(
                title='Cash Flow',
                xaxis_title='Date',
                yaxis_title='Ending Balance',
                yaxis2=dict(
                    title='Income and Outcome',
                    overlaying='y',
                    side='right'
                ),
                legend_title='Category',
                barmode='group'
            )
            profit_loss_fig = go.Figure()
            profit_loss_fig.add_trace(go.Bar(
                x=monthly_df['month'].astype(str),
                y=monthly_df['income'] - monthly_df['outcome'],
                name='Profit/Loss',
                marker_color=['lightgreen' if val >= 0 else 'lightcoral' for val in monthly_df['income'] - monthly_df['outcome']]
            ))
            profit_loss_fig.update_layout(title='Profit/Loss')
            current_month = monthly_df['month'].iloc[-1]
            last_month = monthly_df['month'].iloc[-2]
            current_income = monthly_df[monthly_df['month'] == current_month]['income'].values[0]
            last_month_income = monthly_df[monthly_df['month'] == last_month]['income'].values[0]
            average_income = monthly_df['income'].mean()
            current_outcome = monthly_df[monthly_df['month'] == current_month]['outcome'].values[0]
            last_month_outcome = monthly_df[monthly_df['month'] == last_month]['outcome'].values[0]
            average_outcome = monthly_df['outcome'].mean()
            income_summary_fig = go.Figure()
            income_summary_fig.add_trace(go.Bar(
                y=['Current', 'Last Month', 'Average'],
                x=[current_income, last_month_income, average_income],
                orientation='h',
                marker_color='lightgreen'
            ))
            income_summary_fig.update_layout(
                title='Income Summary',
                xaxis_title='Amount',
                yaxis_title='',
                barmode='stack'
            )
            outcome_summary_fig = go.Figure()
            outcome_summary_fig.add_trace(go.Bar(
                y=['Current', 'Last Month', 'Average'],
                x=[current_outcome, last_month_outcome, average_outcome],
                orientation='h',
                marker_color='lightcoral'
            ))
            outcome_summary_fig.update_layout(
                title='Outcome Summary',
                xaxis_title='Amount',
                yaxis_title='',
                barmode='stack'
            )
            return (
                f'initial balance: {beginning_balance:,.2f}',
                f'total income: {cash_going_in:,.2f}',
                f'total outcome: {cash_going_out:,.2f}',
                f'profit/loss: {profit_loss:,.2f}',
                f'end balance: {ending_balance:,.2f}',
                cash_flow_fig,
                profit_loss_fig,
                income_summary_fig,
                outcome_summary_fig
            )

    def run(self, port=8060):
        self.app.run_server(debug=True, port=port)


class CategoryDashboard():
    def __init__(self, df, categories):

        self.df = df
        self.categories = categories

        self.df['month'] = self.df['date'].dt.to_period('M')
        self.available_months = self.df['month'].astype(str).unique()
        self.available_months_asc = sorted(self.available_months)
        self.available_months_desc = sorted(self.available_months, reverse=True)
        self.category_totals = self.df.groupby('category')['outcome'].sum().sort_values(ascending=False)
        self.color_sequence = px.colors.qualitative.Plotly
        self.color_mapping = {category: self.color_sequence[i % len(self.color_sequence)] for i, category in enumerate(self.categories)}
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.layout()

    def layout(self):
        self.app.layout = html.Div([
            html.H1("Total Expenditures per Month"),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        id='start-month',
                        options=[{'label': month, 'value': month} for month in self.available_months_asc],
                        value=min(self.available_months),
                        clearable=False,
                        style={'width': '100%', 'display': 'inline-block'}
                    ),
                    width=6
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='end-month',
                        options=[{'label': month, 'value': month} for month in self.available_months_desc],
                        value=max(self.available_months),
                        clearable=False,
                        style={'width': '100%', 'display': 'inline-block'}
                    ),
                    width=6
                )
            ]),
            dbc.Row([
                dbc.Col(
                    html.Div(
                        [dbc.Button(category, id={'type': 'category-button', 'index': category}, color=self.color_mapping[category], className="mr-1 mb-1", n_clicks=0) for category in self.categories],
                        id='category-buttons',
                        style={'padding': '10px', 'display': 'flex', 'flex-direction': 'column', 'align-items': 'flex-start', 'overflow-y': 'scroll', 'height': '400px'}
                    ),
                    width=2
                ),
                dbc.Col(
                    dcc.Graph(id='expenditure-bar'),
                    width=9
                )
            ])
        ])
        self.callbacks()

    def callbacks(self):
        @self.app.callback(
            Output({'type': 'category-button', 'index': ALL}, 'color'),
            Input({'type': 'category-button', 'index': ALL}, 'n_clicks'),
            [State({'type': 'category-button', 'index': ALL}, 'children')]
        )
        def toggle_category_buttons(n_clicks_list, children):
            new_colors = [
                self.color_mapping[category] if n_clicks % 2 == 0 else 'secondary'
                for n_clicks, category in zip(n_clicks_list, children)
            ]
            return new_colors

        @self.app.callback(
            Output('expenditure-bar', 'figure'),
            [Input('start-month', 'value'),
             Input('end-month', 'value'),
             Input({'type': 'category-button', 'index': ALL}, 'color')],
            [State({'type': 'category-button', 'index': ALL}, 'children')]
        )
        def update_bar_chart(start_month, end_month, button_colors, categories):
            mask = (self.df['month'].astype(str) >= start_month) & (self.df['month'].astype(str) <= end_month)
            filtered_df = self.df[mask]
            selected_categories = [cat for cat, color in zip(categories, button_colors) if color == 'secondary']
            if selected_categories:
                filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
            grouped_df = filtered_df.groupby(['month', 'category'])['outcome'].sum().reset_index()
            grouped_df['month'] = grouped_df['month'].astype(str)
            fig = px.bar(grouped_df, x='month', y='outcome', color='category', barmode='stack', title='Total Expenditures per Month',
                         category_orders={'category': self.categories}, color_discrete_map=self.color_mapping)
            fig.update_xaxes(categoryorder='category ascending')
            return fig

    def run(self, port=8061):
        self.app.run_server(debug=True, port=port)


