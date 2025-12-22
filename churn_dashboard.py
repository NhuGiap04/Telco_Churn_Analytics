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
    df = pd.read_csv('data/WA_Fn-UseC_-Telco-Customer-Churn.csv')
    
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
    
    # Order: Fiber optic, DSL, No
    service_order = ['Fiber optic', 'DSL', 'No']
    internet_churn['InternetService'] = pd.Categorical(
        internet_churn['InternetService'], 
        categories=service_order, 
        ordered=True
    )
    internet_churn = internet_churn.sort_values('InternetService')
    
    colors = ['#f39c12', '#e74c3c', '#00B894']
    
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
        yaxis=dict(range=[0, max(internet_churn['ChurnRate']) * 1.2]),
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
    
    # Order by contract length
    contract_order = ['Month-to-month', 'One year', 'Two year']
    contract_churn['Contract'] = pd.Categorical(
        contract_churn['Contract'], 
        categories=contract_order, 
        ordered=True
    )
    contract_churn = contract_churn.sort_values('Contract')
    
    colors = ['#e74c3c', '#f39c12', '#00B894']
    
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
        yaxis=dict(range=[0, max(contract_churn['ChurnRate']) * 1.2]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=40),
        height=300,
        font=dict(family='"Segoe UI", sans-serif')
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
        marker_color='#00B894',
        width=0.35
    ))
    
    fig.update_layout(
        xaxis_title='Tenure (months)',
        yaxis_title='Number of Customers',
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=40),
        height=300,
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

def create_ltv_by_internet_service_chart(df):
    """Create line chart of LTV by tenure for each internet service type."""
    # Create 1-year (12-month) tenure bins
    bins = [0, 12, 24, 36, 48, 60, 72]
    labels = ['12', '24', '36', '48', '60', '72']
    
    df_copy = df.copy()
    df_copy['TenureBin'] = pd.cut(df_copy['tenure'], bins=bins, labels=labels, include_lowest=True)
    
    # Calculate average TotalCharges (as LTV proxy) by tenure bin and internet service
    ltv_data = df_copy.groupby(['TenureBin', 'InternetService'], observed=True)['TotalCharges'].mean().reset_index()
    
    # Colors for each internet service
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
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=40),
        height=300,
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

def create_ltv_by_contract_chart(df):
    """Create line chart of LTV by tenure for each contract type."""
    # Create 1-year (12-month) tenure bins
    bins = [0, 12, 24, 36, 48, 60, 72]
    labels = ['12', '24', '36', '48', '60', '72']
    
    df_copy = df.copy()
    df_copy['TenureBin'] = pd.cut(df_copy['tenure'], bins=bins, labels=labels, include_lowest=True)
    
    # Calculate average TotalCharges (as LTV proxy) by tenure bin and contract
    ltv_data = df_copy.groupby(['TenureBin', 'Contract'], observed=True)['TotalCharges'].mean().reset_index()
    
    # Colors for each contract type
    colors = {
        'Month-to-month': '#e74c3c',
        'One year': '#f39c12',
        'Two year': '#00B894'
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
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=40),
        height=300,
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
    
    # =========================================================================
    # HEADER / TITLE SECTION
    # =========================================================================
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
    
    # =========================================================================
    # KPI CARDS ROW
    # =========================================================================
    dbc.Row([
        # KPI Card 1: Total Customers
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2(
                        f"{len(df):,}",
                        style={
                            'color': '#00B894',
                            'fontWeight': '700',
                            'fontSize': '2.5rem',
                            'marginBottom': '5px',
                            'fontFamily': '"Segoe UI", sans-serif'
                        }
                    ),
                    html.P(
                        "Total Customers",
                        style={
                            'color': '#6c757d',
                            'fontSize': '0.95rem',
                            'marginBottom': '0',
                            'fontFamily': '"Segoe UI", sans-serif'
                        }
                    )
                ], style={'textAlign': 'center', 'padding': '25px'})
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
                        f"{(df['ChurnBinary'].sum() / len(df) * 100):.2f}%",
                        style={
                            'color': '#e74c3c',
                            'fontWeight': '700',
                            'fontSize': '2.5rem',
                            'marginBottom': '5px',
                            'fontFamily': '"Segoe UI", sans-serif'
                        }
                    ),
                    html.P(
                        "Churn Rate",
                        style={
                            'color': '#6c757d',
                            'fontSize': '0.95rem',
                            'marginBottom': '0',
                            'fontFamily': '"Segoe UI", sans-serif'
                        }
                    )
                ], style={'textAlign': 'center', 'padding': '25px'})
            ], style={
                'borderRadius': '10px',
                'border': 'none',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
            })
        ], md=3),
        
        # KPI Card 3: Current Revenue (Monthly Charges)
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2(
                        f"${df['MonthlyCharges'].sum():,.0f}",
                        style={
                            'color': '#3498db',
                            'fontWeight': '700',
                            'fontSize': '2.5rem',
                            'marginBottom': '5px',
                            'fontFamily': '"Segoe UI", sans-serif'
                        }
                    ),
                    html.P(
                        "Monthly Revenue",
                        style={
                            'color': '#6c757d',
                            'fontSize': '0.95rem',
                            'marginBottom': '0',
                            'fontFamily': '"Segoe UI", sans-serif'
                        }
                    )
                ], style={'textAlign': 'center', 'padding': '25px'})
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
                        f"{df['tenure'].mean():.1f}",
                        style={
                            'color': '#9b59b6',
                            'fontWeight': '700',
                            'fontSize': '2.5rem',
                            'marginBottom': '5px',
                            'fontFamily': '"Segoe UI", sans-serif'
                        }
                    ),
                    html.P(
                        "Avg Tenure (months)",
                        style={
                            'color': '#6c757d',
                            'fontSize': '0.95rem',
                            'marginBottom': '0',
                            'fontFamily': '"Segoe UI", sans-serif'
                        }
                    )
                ], style={'textAlign': 'center', 'padding': '25px'})
            ], style={
                'borderRadius': '10px',
                'border': 'none',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
            })
        ], md=3),
    ], className='mb-4'),
    
    # =========================================================================
    # CHARTS ROW: Churn Rate by Internet Service, Contract & Tenure
    # =========================================================================
    dbc.Row([
        # Chart 1: Churn Rate by Internet Service
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5(
                        "Churn Rate by Type of Internet Service",
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
                        figure=create_churn_by_internet_chart(df),
                        config={'displayModeBar': False}
                    )
                ])
            ], style={
                'borderRadius': '10px',
                'border': 'none',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
            })
        ], md=4),
        
        # Chart 2: Churn Rate by Contract
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
                        figure=create_churn_by_contract_chart(df),
                        config={'displayModeBar': False}
                    )
                ])
            ], style={
                'borderRadius': '10px',
                'border': 'none',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
            })
        ], md=4),
        
        # Chart 3: Tenure Distribution by Churn Status
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
                        figure=create_tenure_histogram(df),
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
    
    # =========================================================================
    # CHARTS ROW: LTV by Internet Service & Contract
    # =========================================================================
    dbc.Row([
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
                        figure=create_ltv_by_internet_service_chart(df),
                        config={'displayModeBar': False}
                    )
                ])
            ], style={
                'borderRadius': '10px',
                'border': 'none',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
            })
        ], md=6),
        
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
                        figure=create_ltv_by_contract_chart(df),
                        config={'displayModeBar': False}
                    )
                ])
            ], style={
                'borderRadius': '10px',
                'border': 'none',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.08)'
            })
        ], md=6),
    ], className='mb-4'),
    
], fluid=True, style={
    'backgroundColor': '#f0f2f5',
    'minHeight': '100vh',
    'paddingBottom': '30px',
    'paddingLeft': '30px',
    'paddingRight': '30px'
})

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    print("🚀 Starting Telco Churn Analysis Dashboard...")
    print("📊 Open your browser and navigate to: http://127.0.0.1:8050")
    app.run(debug=True)
