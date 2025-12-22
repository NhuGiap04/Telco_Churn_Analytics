"""
Telco Churn Analysis Dashboard
==============================
A comprehensive dashboard for analyzing customer churn
Built with Plotly Dash
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

# ============================================================================
# DATA LOADING & PREPROCESSING
# ============================================================================

def load_and_prepare_data():
    """Load and preprocess the telco churn data."""
    df = pd.read_csv('data/Telco-Customer-Churn.csv')
    
    # Convert TotalCharges to numeric (handle empty strings)
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df['TotalCharges'] = df['TotalCharges'].fillna(0)
    
    # Create binary churn column
    df['ChurnBinary'] = (df['Churn'] == 'Yes').astype(int)
    
    # Create tenure bands
    df['TenureBand'] = pd.cut(
        df['tenure'],
        bins=[0, 3, 6, 12, 24, 48, 72],
        labels=['0-3', '3-6', '6-12', '12-24', '24-48', '48-72'],
        include_lowest=True
    )
    
    # Create segment: Contract × InternetService
    df['Segment'] = df['Contract'] + ' | ' + df['InternetService']
    
    return df

df = load_and_prepare_data()

# ============================================================================
# CHART FUNCTIONS
# ============================================================================

def create_churn_by_internet_chart(df):
    """Create vertical bar chart of churn rate by internet service type."""
    internet_churn = df.groupby('InternetService').agg({
        'ChurnBinary': ['sum', 'count']
    }).reset_index()
    internet_churn.columns = ['InternetService', 'Churners', 'Total']
    internet_churn['ChurnRate'] = internet_churn['Churners'] / internet_churn['Total'] * 100
    
    # Sort by churn rate descending
    internet_churn = internet_churn.sort_values('ChurnRate', ascending=False)
    
    # Use sky blue color for all bars
    colors = ['#87CEEB'] * len(internet_churn)
    
    fig = go.Figure(data=[
        go.Bar(
            x=internet_churn['InternetService'],
            y=internet_churn['ChurnRate'],
            text=[f'{v:.2f}%' for v in internet_churn['ChurnRate']],
            textposition='outside',
            marker_color=colors,
            width=0.5
        )
    ])
    
    fig.update_layout(
        xaxis_title='Internet Service',
        yaxis_title='Churn Rate (%)',
        yaxis=dict(
            range=[0, max(internet_churn['ChurnRate']) * 1.2],
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=40),
        height=300,
        font=dict(family='"Segoe UI", sans-serif')
    )
    
    return fig

def create_churn_by_contract_chart(df):
    """Create vertical bar chart of churn rate by contract type."""
    contract_churn = df.groupby('Contract').agg({
        'ChurnBinary': ['sum', 'count']
    }).reset_index()
    contract_churn.columns = ['Contract', 'Churners', 'Total']
    contract_churn['ChurnRate'] = contract_churn['Churners'] / contract_churn['Total'] * 100
    
    # Sort by churn rate descending
    contract_churn = contract_churn.sort_values('ChurnRate', ascending=False)
    
    # Use sky blue color for all bars
    colors = ['#87CEEB'] * len(contract_churn)
    
    fig = go.Figure(data=[
        go.Bar(
            x=contract_churn['Contract'],
            y=contract_churn['ChurnRate'],
            text=[f'{v:.2f}%' for v in contract_churn['ChurnRate']],
            textposition='outside',
            marker_color=colors,
            width=0.5
        )
    ])
    
    fig.update_layout(
        xaxis_title='Contract Type',
        yaxis_title='Churn Rate (%)',
        yaxis=dict(
            range=[0, max(contract_churn['ChurnRate']) * 1.2],
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=40),
        height=300,
        font=dict(family='"Segoe UI", sans-serif')
    )
    
    return fig

def create_churn_by_payment_method_chart(df):
    """Create vertical bar chart of churn rate by payment method."""
    payment_churn = df.groupby('PaymentMethod').agg({
        'ChurnBinary': ['sum', 'count']
    }).reset_index()
    payment_churn.columns = ['PaymentMethod', 'Churners', 'Total']
    payment_churn['ChurnRate'] = payment_churn['Churners'] / payment_churn['Total'] * 100
    
    # Map payment method names to shorter versions
    name_mapping = {
        'Electronic check': 'Electronic',
        'Mailed check': 'Mailed',
        'Bank transfer (automatic)': 'Bank Transfer',
        'Credit card (automatic)': 'Credit Card'
    }
    payment_churn['PaymentMethodShort'] = payment_churn['PaymentMethod'].map(name_mapping)
    
    # Sort by churn rate descending
    payment_churn = payment_churn.sort_values('ChurnRate', ascending=False)
    
    # Use sky blue color for all bars
    colors = ['#87CEEB'] * len(payment_churn)
    
    fig = go.Figure(data=[
        go.Bar(
            x=payment_churn['PaymentMethodShort'],
            y=payment_churn['ChurnRate'],
            text=[f'{v:.2f}%' for v in payment_churn['ChurnRate']],
            textposition='outside',
            marker_color=colors,
            width=0.5
        )
    ])
    
    fig.update_layout(
        xaxis_title='Payment Method',
        yaxis_title='Churn Rate (%)',
        yaxis=dict(
            range=[0, max(payment_churn['ChurnRate']) * 1.2],
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=40),
        height=300,
        font=dict(family='"Segoe UI", sans-serif'),
        xaxis=dict(tickangle=0)
    )
    
    return fig

def create_tenure_histogram(df):
    """Create histogram of tenure for churned vs stayed customers."""
    # Create tenure bins
    bins = [0, 15, 30, 45, 60, 100]
    labels = ['1-15', '15-30', '30-45', '45-60', '>60']
    
    df_copy = df.copy()
    df_copy['TenureBin'] = pd.cut(df_copy['tenure'], bins=bins, labels=labels, include_lowest=True)
    
    # Group by tenure bin and churn status
    churned = df_copy[df_copy['ChurnBinary'] == 1].groupby('TenureBin', observed=True).size().reindex(labels, fill_value=0)
    stayed = df_copy[df_copy['ChurnBinary'] == 0].groupby('TenureBin', observed=True).size().reindex(labels, fill_value=0)
    
    fig = go.Figure()
    
    # Distinct colors: Churned=red, Stayed=blue
    fig.add_trace(go.Bar(
        x=labels,
        y=churned.values,
        name='Churned',
        marker_color='#e74c3c',
        width=0.35
    ))
    
    fig.add_trace(go.Bar(
        x=labels,
        y=stayed.values,
        name='Stayed',
        marker_color='#0072B2',
        width=0.35
    ))
    
    fig.update_layout(
        xaxis_title='Tenure (months)',
        yaxis_title='Number of Customers',
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=40),
        height=300,
        font=dict(family='"Segoe UI", sans-serif'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.05,
            xanchor='center',
            x=0.5
        )
    )
    
    return fig

def create_ltv_by_internet_service_chart(df):
    """Create line chart of LTV by tenure for each internet service type."""
    # Create 1-year (12-month) tenure bins
    bins = [0, 12, 24, 36, 48, 60, 72]
    labels = ['12', '24', '36', '48', '60', '72']
    
    df_copy = df.copy()
    df_copy['TenureBin'] = pd.cut(df_copy['tenure'], bins=bins, labels=labels, include_lowest=True)
    
    # Calculate average TotalCharges (as LTV proxy) by tenure bin and internet service
    ltv_data = df_copy.groupby(['TenureBin', 'InternetService'], observed=True)['TotalCharges'].mean().reset_index()
    
    # Consistent colors: Fiber optic=red, DSL=orange, No=green
    colors = {
        'Fiber optic': '#e74c3c',
        'DSL': '#f39c12',
        'No': '#00B894'
    }
    
    fig = go.Figure()
    
    for service in ['Fiber optic', 'DSL', 'No']:
        service_data = ltv_data[ltv_data['InternetService'] == service]
        fig.add_trace(go.Scatter(
            x=service_data['TenureBin'].astype(str),
            y=service_data['TotalCharges'],
            mode='lines+markers',
            name=service,
            line=dict(color=colors[service], width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        xaxis_title='Tenure (months)',
        yaxis_title='Average Lifetime Value ($)',
        yaxis=dict(
            range=[0, 8000],
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=40),
        height=300,
        font=dict(family='"Segoe UI", sans-serif'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.05,
            xanchor='center',
            x=0.5
        ),
        shapes=[
            dict(
                type='line',
                x0=0,
                x1=1,
                xref='paper',
                y0=8000,
                y1=8000,
                line=dict(
                    color='rgba(200, 200, 200, 0.4)',
                    width=1
                )
            )
        ]
    )
    
    return fig

def create_ltv_by_contract_chart(df):
    """Create line chart of LTV by tenure for each contract type."""
    # Create 1-year (12-month) tenure bins
    bins = [0, 12, 24, 36, 48, 60, 72]
    labels = ['12', '24', '36', '48', '60', '72']
    
    df_copy = df.copy()
    df_copy['TenureBin'] = pd.cut(df_copy['tenure'], bins=bins, labels=labels, include_lowest=True)
    
    # Calculate average TotalCharges (as LTV proxy) by tenure bin and contract
    ltv_data = df_copy.groupby(['TenureBin', 'Contract'], observed=True)['TotalCharges'].mean().reset_index()
    
    # Distinct colors: Month-to-month=blue, One year=purple, Two year=teal
    colors = {
        'Month-to-month': '#3498db',
        'One year': '#9b59b6',
        'Two year': '#1abc9c'
    }
    
    fig = go.Figure()
    
    for contract in ['Month-to-month', 'One year', 'Two year']:
        contract_data = ltv_data[ltv_data['Contract'] == contract]
        fig.add_trace(go.Scatter(
            x=contract_data['TenureBin'].astype(str),
            y=contract_data['TotalCharges'],
            mode='lines+markers',
            name=contract,
            line=dict(color=colors[contract], width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        xaxis_title='Tenure (months)',
        yaxis_title='Average Lifetime Value ($)',
        yaxis=dict(
            range=[0, 8000],
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=40),
        height=300,
        font=dict(family='"Segoe UI", sans-serif'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.05,
            xanchor='center',
            x=0.5
        ),
        shapes=[
            dict(
                type='line',
                x0=0,
                x1=1,
                xref='paper',
                y0=8000,
                y1=8000,
                line=dict(
                    color='rgba(200, 200, 200, 0.4)',
                    width=1
                )
            )
        ]
    )
    
    return fig

# ============================================================================
# DASH APP SETUP
# ============================================================================

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Telco Churn Analysis"

# ============================================================================
# SIDEBAR FILTER SECTION
# ============================================================================

sidebar_style = {
    'backgroundColor': '#2c3e50',
    'padding': '20px',
    'borderRadius': '10px',
    'height': '100%',
    'minHeight': 'calc(100vh - 60px)'
}

filter_label_style = {
    'color': '#ffffff',
    'fontWeight': '600',
    'fontSize': '0.85rem',
    'marginBottom': '8px',
    'fontFamily': '"Segoe UI", sans-serif',
    'textTransform': 'uppercase',
    'letterSpacing': '0.5px'
}

sidebar = html.Div([
    # Gender Filter
    html.Div([
        html.Label("Gender", style=filter_label_style),
        dcc.Dropdown(
            id='gender-filter',
            options=[
                {'label': 'All', 'value': 'All'},
                {'label': 'Male', 'value': 'Male'},
                {'label': 'Female', 'value': 'Female'}
            ],
            value='All',
            clearable=False,
            style={'fontFamily': '"Segoe UI", sans-serif'}
        )
    ], style={'marginBottom': '20px'}),
    
    # Paperless Billing Filter
    html.Div([
        html.Label("Paperless Billing", style=filter_label_style),
        dcc.Dropdown(
            id='paperless-filter',
            options=[
                {'label': 'All', 'value': 'All'},
                {'label': 'Yes', 'value': 'Yes'},
                {'label': 'No', 'value': 'No'}
            ],
            value='All',
            clearable=False,
            style={'fontFamily': '"Segoe UI", sans-serif'}
        )
    ], style={'marginBottom': '20px'}),
    
    # Phone Service Filter
    html.Div([
        html.Label("Phone Service", style=filter_label_style),
        dcc.Dropdown(
            id='phone-filter',
            options=[
                {'label': 'All', 'value': 'All'},
                {'label': 'Yes', 'value': 'Yes'},
                {'label': 'No', 'value': 'No'}
            ],
            value='All',
            clearable=False,
            style={'fontFamily': '"Segoe UI", sans-serif'}
        )
    ], style={'marginBottom': '20px'}),
    
    # Dependents Filter
    html.Div([
        html.Label("Dependents", style=filter_label_style),
        dcc.Dropdown(
            id='dependents-filter',
            options=[
                {'label': 'All', 'value': 'All'},
                {'label': 'Yes', 'value': 'Yes'},
                {'label': 'No', 'value': 'No'}
            ],
            value='All',
            clearable=False,
            style={'fontFamily': '"Segoe UI", sans-serif'}
        )
    ], style={'marginBottom': '20px'}),
    
    # Tenure Filter
    html.Div([
        html.Label("Tenure (months)", style=filter_label_style),
        html.Div([
            dcc.Input(
                id='tenure-min',
                type='number',
                placeholder='Min',
                min=0,
                max=72,
                value=0,
                style={
                    'width': '48%',
                    'marginRight': '4%',
                    'fontFamily': '"Segoe UI", sans-serif',
                    'padding': '8px',
                    'borderRadius': '4px',
                    'border': '1px solid #ccc'
                }
            ),
            dcc.Input(
                id='tenure-max',
                type='number',
                placeholder='Max',
                min=0,
                max=72,
                value=72,
                style={
                    'width': '48%',
                    'fontFamily': '"Segoe UI", sans-serif',
                    'padding': '8px',
                    'borderRadius': '4px',
                    'border': '1px solid #ccc'
                }
            )
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
    ], style={'marginBottom': '25px'}),
    
    # Reset Button
    html.Div([
        dbc.Button(
            "Reset Filters",
            id='reset-filters',
            color='success',
            outline=True,
            style={
                'width': '100%',
                'fontFamily': '"Segoe UI", sans-serif',
                'fontWeight': '600'
            }
        )
    ], style={'marginTop': '20px'})
    
], style=sidebar_style)

# ============================================================================
# LAYOUT
# ============================================================================

app.layout = dbc.Container([
    # =================================================================
    # HEADER / TITLE SECTION (FULL WIDTH)
    # =================================================================
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1(
                    "TELCO CHURN ANALYSIS",
                    style={
                        'textAlign': 'left',
                        'color': '#FFFFFF',
                        'fontWeight': '700',
                        'fontSize': '1.5rem',
                        'marginBottom': '0',
                        'letterSpacing': '0.5px',
                        'textTransform': 'uppercase',
                        'fontFamily': '"Segoe UI", sans-serif'
                    }
                )
            ], style={
                'backgroundColor': '#00B894',
                'padding': '15px 25px',
                'borderRadius': '8px'
            })
        ])
    ], className='mb-4'),
    
    dbc.Row([
        # =====================================================================
        # LEFT SIDEBAR - FILTERS
        # =====================================================================
        dbc.Col([
            sidebar
        ], md=2, style={'paddingRight': '10px'}),
        
        # =====================================================================
        # MAIN CONTENT AREA
        # =====================================================================
        dbc.Col([
            # =================================================================
            # KPI CARDS ROW
            # =================================================================
            dbc.Row([
                # KPI Card 1: Total Customers
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(
                                id='kpi-total-customers',
                                style={
                                    'color': '#00B894',
                                    'fontWeight': '700',
                                    'fontSize': '2rem',
                                    'marginBottom': '5px',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            ),
                            html.P(
                                "Total Customers",
                                style={
                                    'color': '#6c757d',
                                    'fontSize': '0.85rem',
                                    'marginBottom': '0',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            )
                        ], style={'textAlign': 'center', 'padding': '20px'})
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
                    })
                ], md=3),
                
                # KPI Card 2: Churn Rate
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(
                                id='kpi-churn-rate',
                                style={
                                    'color': '#e74c3c',
                                    'fontWeight': '700',
                                    'fontSize': '2rem',
                                    'marginBottom': '5px',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            ),
                            html.P(
                                "Churn Rate",
                                style={
                                    'color': '#6c757d',
                                    'fontSize': '0.85rem',
                                    'marginBottom': '0',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            )
                        ], style={'textAlign': 'center', 'padding': '20px'})
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
                    })
                ], md=3),
                
                # KPI Card 3: Monthly Revenue
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(
                                id='kpi-monthly-revenue',
                                style={
                                    'color': '#3498db',
                                    'fontWeight': '700',
                                    'fontSize': '2rem',
                                    'marginBottom': '5px',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            ),
                            html.P(
                                "Monthly Revenue",
                                style={
                                    'color': '#6c757d',
                                    'fontSize': '0.85rem',
                                    'marginBottom': '0',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            )
                        ], style={'textAlign': 'center', 'padding': '20px'})
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
                    })
                ], md=3),
                
                # KPI Card 4: Average Tenure
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(
                                id='kpi-avg-tenure',
                                style={
                                    'color': '#9b59b6',
                                    'fontWeight': '700',
                                    'fontSize': '2rem',
                                    'marginBottom': '5px',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            ),
                            html.P(
                                "Avg Tenure (months)",
                                style={
                                    'color': '#6c757d',
                                    'fontSize': '0.85rem',
                                    'marginBottom': '0',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            )
                        ], style={'textAlign': 'center', 'padding': '20px'})
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
                    })
                ], md=3),
            ], className='mb-4'),
            
            # =================================================================
            # CHARTS ROW 1: Churn Rate Charts
            # =================================================================
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(
                                "Churn Rate by Internet Service",
                                style={
                                    'textAlign': 'center',
                                    'color': '#2c3e50',
                                    'fontWeight': '600',
                                    'marginBottom': '15px',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            ),
                            dcc.Graph(
                                id='churn-by-internet-chart',
                                config={'displayModeBar': False}
                            )
                        ])
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
                    })
                ], md=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(
                                "Churn Rate by Contract",
                                style={
                                    'textAlign': 'center',
                                    'color': '#2c3e50',
                                    'fontWeight': '600',
                                    'marginBottom': '15px',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            ),
                            dcc.Graph(
                                id='churn-by-contract-chart',
                                config={'displayModeBar': False}
                            )
                        ])
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
                    })
                ], md=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(
                                "Churn Rate by Payment Method",
                                style={
                                    'textAlign': 'center',
                                    'color': '#2c3e50',
                                    'fontWeight': '600',
                                    'marginBottom': '15px',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            ),
                            dcc.Graph(
                                id='churn-by-payment-chart',
                                config={'displayModeBar': False}
                            )
                        ])
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
                    })
                ], md=4),
            ], className='mb-4'),
            
            # =================================================================
            # CHARTS ROW 2: Tenure Distribution & LTV Charts
            # =================================================================
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(
                                "Tenure Distribution (Churned vs Stayed)",
                                style={
                                    'textAlign': 'center',
                                    'color': '#2c3e50',
                                    'fontWeight': '600',
                                    'marginBottom': '15px',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            ),
                            dcc.Graph(
                                id='tenure-histogram',
                                config={'displayModeBar': False}
                            )
                        ])
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
                    })
                ], md=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(
                                "Lifetime Value by Internet Service",
                                style={
                                    'textAlign': 'center',
                                    'color': '#2c3e50',
                                    'fontWeight': '600',
                                    'marginBottom': '15px',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            ),
                            dcc.Graph(
                                id='ltv-by-internet-chart',
                                config={'displayModeBar': False}
                            )
                        ])
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
                    })
                ], md=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(
                                "Lifetime Value by Contract",
                                style={
                                    'textAlign': 'center',
                                    'color': '#2c3e50',
                                    'fontWeight': '600',
                                    'marginBottom': '15px',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            ),
                            dcc.Graph(
                                id='ltv-by-contract-chart',
                                config={'displayModeBar': False}
                            )
                        ])
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
                    })
                ], md=4),
            ], className='mb-4'),
            
        ], md=10, style={'paddingLeft': '10px'})
    ])
    
], fluid=True, style={
    'backgroundColor': '#f0f2f5',
    'minHeight': '100vh',
    'paddingTop': '20px',
    'paddingBottom': '30px',
    'paddingLeft': '20px',
    'paddingRight': '20px'
})

# ============================================================================
# CALLBACKS
# ============================================================================

def filter_data(gender_filter, paperless_filter, phone_filter, dependents_filter, tenure_min, tenure_max):
    """Filter dataframe based on sidebar selections."""
    filtered_df = df.copy()
    
    if gender_filter != 'All':
        filtered_df = filtered_df[filtered_df['gender'] == gender_filter]
    
    if paperless_filter != 'All':
        filtered_df = filtered_df[filtered_df['PaperlessBilling'] == paperless_filter]
    
    if phone_filter != 'All':
        filtered_df = filtered_df[filtered_df['PhoneService'] == phone_filter]
    
    if dependents_filter != 'All':
        filtered_df = filtered_df[filtered_df['Dependents'] == dependents_filter]
    
    # Apply tenure filter
    if tenure_min is not None and tenure_max is not None:
        filtered_df = filtered_df[(filtered_df['tenure'] >= tenure_min) & 
                                   (filtered_df['tenure'] <= tenure_max)]
    
    return filtered_df

@app.callback(
    [Output('kpi-total-customers', 'children'),
     Output('kpi-churn-rate', 'children'),
     Output('kpi-monthly-revenue', 'children'),
     Output('kpi-avg-tenure', 'children'),
     Output('churn-by-internet-chart', 'figure'),
     Output('churn-by-contract-chart', 'figure'),
     Output('churn-by-payment-chart', 'figure'),
     Output('tenure-histogram', 'figure'),
     Output('ltv-by-internet-chart', 'figure'),
     Output('ltv-by-contract-chart', 'figure')],
    [Input('gender-filter', 'value'),
     Input('paperless-filter', 'value'),
     Input('phone-filter', 'value'),
     Input('dependents-filter', 'value'),
     Input('tenure-min', 'value'),
     Input('tenure-max', 'value')]
)
def update_dashboard(gender_filter, paperless_filter, phone_filter, dependents_filter, tenure_min, tenure_max):
    """Update all dashboard components based on filter selections."""
    filtered_df = filter_data(gender_filter, paperless_filter, phone_filter, dependents_filter, tenure_min, tenure_max)
    
    # Calculate KPIs
    total_customers = f"{len(filtered_df):,}"
    
    if len(filtered_df) > 0:
        churn_rate = f"{(filtered_df['ChurnBinary'].sum() / len(filtered_df) * 100):.2f}%"
        monthly_revenue = f"${filtered_df['MonthlyCharges'].sum():,.0f}"
        avg_tenure = f"{filtered_df['tenure'].mean():.1f}"
    else:
        churn_rate = "0%"
        monthly_revenue = "$0"
        avg_tenure = "0"
    
    # Generate charts with filtered data
    internet_chart = create_churn_by_internet_chart(filtered_df) if len(filtered_df) > 0 else go.Figure()
    contract_chart = create_churn_by_contract_chart(filtered_df) if len(filtered_df) > 0 else go.Figure()
    payment_chart = create_churn_by_payment_method_chart(filtered_df) if len(filtered_df) > 0 else go.Figure()
    tenure_chart = create_tenure_histogram(filtered_df) if len(filtered_df) > 0 else go.Figure()
    ltv_internet_chart = create_ltv_by_internet_service_chart(filtered_df) if len(filtered_df) > 0 else go.Figure()
    ltv_contract_chart = create_ltv_by_contract_chart(filtered_df) if len(filtered_df) > 0 else go.Figure()
    
    return (total_customers, churn_rate, monthly_revenue, avg_tenure,
            internet_chart, contract_chart, payment_chart, tenure_chart,
            ltv_internet_chart, ltv_contract_chart)

@app.callback(
    [Output('gender-filter', 'value'),
     Output('paperless-filter', 'value'),
     Output('phone-filter', 'value'),
     Output('dependents-filter', 'value'),
     Output('tenure-min', 'value'),
     Output('tenure-max', 'value')],
    [Input('reset-filters', 'n_clicks')],
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    """Reset all filters to default values."""
    return 'All', 'All', 'All', 'All', 0, 72

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    print("🚀 Starting Telco Churn Analysis Dashboard...")
    print("📊 Open your browser and navigate to: http://127.0.0.1:8050")
    app.run(debug=True)
