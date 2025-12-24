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
from plotly.subplots import make_subplots
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

def create_tenure_distribution_chart(df):
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
            range=[0, 1500],
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
            dtick=500
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
        ),
        shapes=[
            dict(
                type='line',
                x0=0,
                x1=1,
                xref='paper',
                y0=1500,
                y1=1500,
                line=dict(
                    color='rgba(200, 200, 200, 0.4)',
                    width=1
                )
            )
        ]
    )
    
    return fig

def create_ltv_comparison_chart(df):
    """Create line chart comparing LTV by month-to-month contract and fiber optic over tenure (6 yearly bins)."""
    df_copy = df.copy()
    df_copy['LTV'] = df_copy['tenure'] * df_copy['MonthlyCharges']
    
    # Create 6 tenure bins (1 year each)
    bins = [0, 12, 24, 36, 48, 60, 72]
    labels = ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5', 'Year 6']
    df_copy['TenureBin'] = pd.cut(df_copy['tenure'], bins=bins, labels=labels, include_lowest=True)
    
    fig = go.Figure()
    
    # Month-to-month contract LTV
    mtm_df = df_copy[df_copy['Contract'] == 'Month-to-month'].copy()
    if len(mtm_df) > 0:
        mtm_grouped = mtm_df.groupby('TenureBin', observed=True)['LTV'].mean().reindex(labels, fill_value=0)
        fig.add_trace(go.Scatter(
            x=labels,
            y=mtm_grouped.values,
            name='Month-to-Month',
            mode='lines+markers',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8)
        ))
    
    # Fiber optic internet service LTV
    fiber_df = df_copy[df_copy['InternetService'] == 'Fiber optic'].copy()
    if len(fiber_df) > 0:
        fiber_grouped = fiber_df.groupby('TenureBin', observed=True)['LTV'].mean().reindex(labels, fill_value=0)
        fig.add_trace(go.Scatter(
            x=labels,
            y=fiber_grouped.values,
            name='Fiber Optic',
            mode='lines+markers',
            line=dict(color='#2ecc71', width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        xaxis_title='Tenure Period',
        yaxis_title='Average LTV ($)',
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=40, t=20, b=40),
        height=400,
        font=dict(family='"Segoe UI", sans-serif'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )
    
    return fig

def create_ltv_by_service_bundle_chart(df):
    """Create diverging horizontal bar chart showing actual LTV (right) and lost potential LTV (left) by service bundle."""
    # Calculate actual LTV as tenure × monthly charges
    df_copy = df.copy()
    df_copy['ActualLTV'] = df_copy['tenure'] * df_copy['MonthlyCharges']
    
    # Create service bundle combination
    df_copy['ServiceBundle'] = df_copy['InternetService'] + ' | ' + df_copy['Contract']
    
    # Calculate average actual LTV and average monthly charges for each service bundle
    ltv_by_bundle = df_copy.groupby('ServiceBundle').agg({
        'ActualLTV': 'mean',
        'MonthlyCharges': 'mean'
    }).reset_index()
    
    # Calculate expected LTV if customers stayed for 72 months
    ltv_by_bundle['ExpectedLTV72'] = ltv_by_bundle['MonthlyCharges'] * 72
    
    # Calculate lost LTV (potential - actual) as negative for left side
    ltv_by_bundle['LostLTV'] = -(ltv_by_bundle['ExpectedLTV72'] - ltv_by_bundle['ActualLTV'])
    
    # Sort by actual LTV (ascending for horizontal bars)
    ltv_by_bundle = ltv_by_bundle.sort_values('ActualLTV', ascending=True)
    
    fig = go.Figure()
    
    # Add lost potential LTV (red bars, on left/negative side)
    fig.add_trace(go.Bar(
        x=ltv_by_bundle['LostLTV'],
        y=ltv_by_bundle['ServiceBundle'],
        orientation='h',
        name='Lost Potential LTV',
        marker_color='#e74c3c'
    ))
    
    # Add actual LTV (blue bars, on right/positive side)
    fig.add_trace(go.Bar(
        x=ltv_by_bundle['ActualLTV'],
        y=ltv_by_bundle['ServiceBundle'],
        orientation='h',
        name='Actual LTV',
        marker_color='#0072B2'
    ))
    
    # Calculate max value for symmetric axis
    max_val = max(abs(ltv_by_bundle['LostLTV'].min()), ltv_by_bundle['ActualLTV'].max())
    
    fig.update_layout(
        xaxis_title='Lifetime Value ($)',
        yaxis_title='Internet Service & Contract',
        xaxis=dict(
            range=[-max_val * 1.1, max_val * 1.1],
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
            zeroline=True,
            zerolinecolor='rgba(0, 0, 0, 0.5)',
            zerolinewidth=2
        ),
        yaxis=dict(
            ticksuffix='  '
        ),
        barmode='relative',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=250, r=80, t=20, b=40),
        height=400,
        font=dict(family='"Segoe UI", sans-serif'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )
    
    return fig

# ============================================================================
# DASH APP SETUP
# ============================================================================

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Telco Churn Analysis"

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
    
    # =================================================================
    # KPI CARDS AND FILTERS ROW
    # =================================================================
    dbc.Row([
        # KPIs on the left
        dbc.Col([
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
                        ], style={'textAlign': 'center', 'padding': '20px 10px'})
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                        'height': '100%'
                    })
                ], md=6),
                
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
                        ], style={'textAlign': 'center', 'padding': '20px 10px'})
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                        'height': '100%'
                    })
                ], md=6),
            ], className='mb-2'),
            
            dbc.Row([
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
                        ], style={'textAlign': 'center', 'padding': '20px 10px'})
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                        'height': '100%'
                    })
                ], md=6),
                
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
                        ], style={'textAlign': 'center', 'padding': '20px 10px'})
                    ], style={
                        'borderRadius': '10px',
                        'border': 'none',
                        'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                        'height': '100%'
                    })
                ], md=6),
            ])
        ], md=5),
        
        # Filters on the right (horizontal layout)
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        # Gender Filter
                        dbc.Col([
                            html.Label("Gender", style={
                                'color': '#2c3e50',
                                'fontWeight': '600',
                                'fontSize': '0.7rem',
                                'marginBottom': '3px',
                                'fontFamily': '"Segoe UI", sans-serif'
                            }),
                            dcc.Dropdown(
                                id='gender-filter',
                                options=[
                                    {'label': 'All', 'value': 'All'},
                                    {'label': 'Male', 'value': 'Male'},
                                    {'label': 'Female', 'value': 'Female'}
                                ],
                                value='All',
                                clearable=False,
                                style={'fontFamily': '"Segoe UI", sans-serif', 'fontSize': '0.8rem'}
                            )
                        ], md=3),
                        
                        # Paperless Billing Filter
                        dbc.Col([
                            html.Label("Paperless Billing", style={
                                'color': '#2c3e50',
                                'fontWeight': '600',
                                'fontSize': '0.7rem',
                                'marginBottom': '3px',
                                'fontFamily': '"Segoe UI", sans-serif'
                            }),
                            dcc.Dropdown(
                                id='paperless-filter',
                                options=[
                                    {'label': 'All', 'value': 'All'},
                                    {'label': 'Yes', 'value': 'Yes'},
                                    {'label': 'No', 'value': 'No'}
                                ],
                                value='All',
                                clearable=False,
                                style={'fontFamily': '"Segoe UI", sans-serif', 'fontSize': '0.8rem'}
                            )
                        ], md=3),
                        
                        # Phone Service Filter
                        dbc.Col([
                            html.Label("Phone Service", style={
                                'color': '#2c3e50',
                                'fontWeight': '600',
                                'fontSize': '0.7rem',
                                'marginBottom': '3px',
                                'fontFamily': '"Segoe UI", sans-serif'
                            }),
                            dcc.Dropdown(
                                id='phone-filter',
                                options=[
                                    {'label': 'All', 'value': 'All'},
                                    {'label': 'Yes', 'value': 'Yes'},
                                    {'label': 'No', 'value': 'No'}
                                ],
                                value='All',
                                clearable=False,
                                style={'fontFamily': '"Segoe UI", sans-serif', 'fontSize': '0.8rem'}
                            )
                        ], md=3),
                        
                        # Dependents Filter
                        dbc.Col([
                            html.Label("Dependents", style={
                                'color': '#2c3e50',
                                'fontWeight': '600',
                                'fontSize': '0.7rem',
                                'marginBottom': '3px',
                                'fontFamily': '"Segoe UI", sans-serif'
                            }),
                            dcc.Dropdown(
                                id='dependents-filter',
                                options=[
                                    {'label': 'All', 'value': 'All'},
                                    {'label': 'Yes', 'value': 'Yes'},
                                    {'label': 'No', 'value': 'No'}
                                ],
                                value='All',
                                clearable=False,
                                style={'fontFamily': '"Segoe UI", sans-serif', 'fontSize': '0.8rem'}
                            )
                        ], md=3),
                    ], className='mb-2'),
                    
                    # Reset Button
                    dbc.Row([
                        dbc.Col([
                            html.Button(
                                'Reset Filters',
                                id='reset-filters',
                                n_clicks=0,
                                style={
                                    'width': '100%',
                                    'backgroundColor': '#00B894',
                                    'color': 'white',
                                    'border': 'none',
                                    'borderRadius': '5px',
                                    'padding': '6px 15px',
                                    'cursor': 'pointer',
                                    'fontWeight': '600',
                                    'fontSize': '0.8rem',
                                    'fontFamily': '"Segoe UI", sans-serif'
                                }
                            )
                        ], md=12)
                    ])
                ], style={'padding': '15px'})
            ], style={
                'borderRadius': '10px',
                'border': 'none',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                'height': '100%'
            })
        ], md=7)
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
                        id='tenure-distribution-chart',
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
                        "Average Lifetime Value by Internet Service & Contract",
                        style={
                            'textAlign': 'center',
                            'color': '#2c3e50',
                            'fontWeight': '600',
                            'marginBottom': '15px',
                            'fontFamily': '"Segoe UI", sans-serif'
                        }
                    ),
                    dcc.Graph(
                        id='ltv-by-bundle-chart',
                        config={'displayModeBar': False}
                    )
                ])
            ], style={
                'borderRadius': '10px',
                'border': 'none',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
            })
        ], md=8),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5(
                        "LTV Comparison: Month-to-Month vs Fiber Optic",
                        style={
                            'textAlign': 'center',
                            'color': '#2c3e50',
                            'fontWeight': '600',
                            'marginBottom': '15px',
                            'fontFamily': '"Segoe UI", sans-serif'
                        }
                    ),
                    dcc.Graph(
                        id='ltv-customer-count-chart',
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

def filter_data(gender_filter, paperless_filter, phone_filter, dependents_filter):
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
    
    return filtered_df

@app.callback(
    [Output('kpi-total-customers', 'children'),
     Output('kpi-churn-rate', 'children'),
     Output('kpi-monthly-revenue', 'children'),
     Output('kpi-avg-tenure', 'children'),
     Output('churn-by-internet-chart', 'figure'),
     Output('churn-by-contract-chart', 'figure'),
     Output('tenure-distribution-chart', 'figure'),
     Output('ltv-customer-count-chart', 'figure'),
     Output('ltv-by-bundle-chart', 'figure')],
    [Input('gender-filter', 'value'),
     Input('paperless-filter', 'value'),
     Input('phone-filter', 'value'),
     Input('dependents-filter', 'value')]
)
def update_dashboard(gender_filter, paperless_filter, phone_filter, dependents_filter):
    """Update all dashboard components based on filter selections."""
    filtered_df = filter_data(gender_filter, paperless_filter, phone_filter, dependents_filter)
    
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
    tenure_chart = create_tenure_distribution_chart(filtered_df) if len(filtered_df) > 0 else go.Figure()
    ltv_comparison_chart = create_ltv_comparison_chart(filtered_df) if len(filtered_df) > 0 else go.Figure()
    ltv_bundle_chart = create_ltv_by_service_bundle_chart(filtered_df) if len(filtered_df) > 0 else go.Figure()
    
    return (total_customers, churn_rate, monthly_revenue, avg_tenure,
            internet_chart, contract_chart, tenure_chart, ltv_comparison_chart,
            ltv_bundle_chart)

@app.callback(
    [Output('gender-filter', 'value'),
     Output('paperless-filter', 'value'),
     Output('phone-filter', 'value'),
     Output('dependents-filter', 'value')],
    [Input('reset-filters', 'n_clicks')],
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    """Reset all filters to default values."""
    return 'All', 'All', 'All', 'All'

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    print("🚀 Starting Telco Churn Analysis Dashboard...")
    print("📊 Open your browser and navigate to: http://127.0.0.1:8050")
    app.run(debug=True)
