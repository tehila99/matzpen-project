"""
Interactive Dashboard - Stage B
================================
Plotly Dash-based interactive dashboard for intelligence reports analysis.

Features:
1. Load Status: Report distribution by date and urgency
2. Reliability Analysis: Distribution and metrics
3. Intelligence Potential: Geographic keyword analysis
4. Drill-down: Filters and interactive table

Author: Compass Project
Date: December 2025
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, dash_table
from datetime import datetime
import re


# Initialize the Dash app
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Compass Intelligence Dashboard"


def load_data():
    """Load cleaned reports data."""
    df = pd.read_csv('data/processed/clean_reports.csv')
    
    # Parse dates
    df['Source_Date'] = pd.to_datetime(df['Source_Date'], format='%d/%m/%Y %H:%M', errors='coerce')
    df['Date_Only'] = df['Source_Date'].dt.date
    
    # Add geographic keyword detection
    geographic_patterns = [
        r'נ\.צ\.?',
        r'נקודת ציון',
        r'מיקום',
        r'קואורדינטות',
        r'\d{6}',  # 6-digit coordinates
    ]
    
    def has_geographic_keywords(text):
        if pd.isna(text):
            return False
        text_str = str(text)
        for pattern in geographic_patterns:
            if re.search(pattern, text_str):
                return True
        return False
    
    df['Has_Geographic_Keywords'] = df['Content_Body'].apply(has_geographic_keywords)
    
    return df


# Load data
df = load_data()


# Define color schemes
color_scheme = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff7f0e',
    'info': '#17becf'
}


# App Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Compass Intelligence Dashboard", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
        html.P("Interactive Analysis of Intelligence Reports", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '18px'}),
    ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'marginBottom': '20px'}),
    
    # Key Metrics Row
    html.Div([
        html.Div([
            html.H3(f"{len(df):,}", style={'color': color_scheme['primary'], 'marginBottom': '5px'}),
            html.P("Total Reports", style={'color': '#7f8c8d'})
        ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white', 
                  'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'flex': '1', 'margin': '10px'}),
        
        html.Div([
            html.H3(f"{df['Sector'].nunique()}", style={'color': color_scheme['success'], 'marginBottom': '5px'}),
            html.P("Active Sectors", style={'color': '#7f8c8d'})
        ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white', 
                  'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'flex': '1', 'margin': '10px'}),
        
        html.Div([
            html.H3(f"{df['Unit_Name'].nunique()}", style={'color': color_scheme['warning'], 'marginBottom': '5px'}),
            html.P("Units", style={'color': '#7f8c8d'})
        ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white', 
                  'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'flex': '1', 'margin': '10px'}),
        
        html.Div([
            html.H3(f"{df['Has_Geographic_Keywords'].sum():,}", style={'color': color_scheme['info'], 'marginBottom': '5px'}),
            html.P("With Geographic Info", style={'color': '#7f8c8d'})
        ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white', 
                  'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'flex': '1', 'margin': '10px'}),
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),
    
    # Filters Section
    html.Div([
        html.H3("Filters", style={'color': '#2c3e50'}),
        html.Div([
            html.Div([
                html.Label("Sector:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='sector-filter',
                    options=[{'label': 'All Sectors', 'value': 'ALL'}] + 
                            [{'label': sector, 'value': sector} for sector in sorted(df['Sector'].unique())],
                    value='ALL',
                    style={'width': '100%'}
                )
            ], style={'flex': '1', 'marginRight': '10px'}),
            
            html.Div([
                html.Label("Unit:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='unit-filter',
                    options=[{'label': 'All Units', 'value': 'ALL'}] + 
                            [{'label': unit, 'value': unit} for unit in sorted(df['Unit_Name'].unique())],
                    value='ALL',
                    style={'width': '100%'}
                )
            ], style={'flex': '1', 'marginRight': '10px'}),
            
            html.Div([
                html.Label("Urgency:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='urgency-filter',
                    options=[{'label': 'All Urgencies', 'value': 'ALL'}] + 
                            [{'label': urgency, 'value': urgency} for urgency in sorted(df['Report_Urgency'].unique())],
                    value='ALL',
                    style={'width': '100%'}
                )
            ], style={'flex': '1'}),
        ], style={'display': 'flex', 'marginBottom': '20px'}),
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 
              'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
    
    # Section 1: Load Status
    html.Div([
        html.H2("1. Load Status Analysis", style={'color': '#2c3e50', 'borderBottom': '2px solid #3498db', 'paddingBottom': '10px'}),
        
        html.Div([
            html.Div([
                dcc.Graph(id='reports-over-time')
            ], style={'flex': '1', 'marginRight': '10px'}),
            
            html.Div([
                dcc.Graph(id='urgency-distribution')
            ], style={'flex': '1'}),
        ], style={'display': 'flex', 'marginBottom': '20px'}),
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 
              'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
    
    # Section 2: Reliability Analysis
    html.Div([
        html.H2("2. Reliability Analysis", style={'color': '#2c3e50', 'borderBottom': '2px solid #2ecc71', 'paddingBottom': '10px'}),
        
        html.Div([
            html.Div([
                dcc.Graph(id='reliability-pie')
            ], style={'flex': '1', 'marginRight': '10px'}),
            
            html.Div([
                dcc.Graph(id='reliability-bar')
            ], style={'flex': '1'}),
        ], style={'display': 'flex', 'marginBottom': '20px'}),
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 
              'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
    
    # Section 3: Intelligence Potential
    html.Div([
        html.H2("3. Intelligence Potential", style={'color': '#2c3e50', 'borderBottom': '2px solid #e74c3c', 'paddingBottom': '10px'}),
        
        html.Div([
            html.Div([
                dcc.Graph(id='geographic-comparison')
            ], style={'flex': '1', 'marginRight': '10px'}),
            
            html.Div([
                dcc.Graph(id='sector-geographic')
            ], style={'flex': '1'}),
        ], style={'display': 'flex', 'marginBottom': '20px'}),
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 
              'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
    
    # Section 4: Data Table
    html.Div([
        html.H2("4. Detailed Reports", style={'color': '#2c3e50', 'borderBottom': '2px solid #9b59b6', 'paddingBottom': '10px'}),
        html.P("Showing filtered reports (first 100 rows):", style={'color': '#7f8c8d', 'marginBottom': '10px'}),
        html.Div(id='reports-table-container')
    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 
              'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
    
], style={'backgroundColor': '#f5f5f5', 'padding': '20px', 'fontFamily': 'Arial, sans-serif'})


# Callback to filter data
@app.callback(
    [Output('reports-over-time', 'figure'),
     Output('urgency-distribution', 'figure'),
     Output('reliability-pie', 'figure'),
     Output('reliability-bar', 'figure'),
     Output('geographic-comparison', 'figure'),
     Output('sector-geographic', 'figure'),
     Output('reports-table-container', 'children')],
    [Input('sector-filter', 'value'),
     Input('unit-filter', 'value'),
     Input('urgency-filter', 'value')]
)
def update_dashboard(sector, unit, urgency):
    # Filter data
    filtered_df = df.copy()
    
    if sector != 'ALL':
        filtered_df = filtered_df[filtered_df['Sector'] == sector]
    if unit != 'ALL':
        filtered_df = filtered_df[filtered_df['Unit_Name'] == unit]
    if urgency != 'ALL':
        filtered_df = filtered_df[filtered_df['Report_Urgency'] == urgency]
    
    # 1. Reports over time
    reports_by_date = filtered_df.groupby('Date_Only').size().reset_index(name='Count')
    reports_by_date = reports_by_date.sort_values('Date_Only')
    
    fig_timeline = px.line(
        reports_by_date, 
        x='Date_Only', 
        y='Count',
        title='Report Distribution Over Time',
        labels={'Date_Only': 'Date', 'Count': 'Number of Reports'},
        template='plotly_white'
    )
    fig_timeline.update_traces(line_color=color_scheme['primary'], line_width=2)
    fig_timeline.update_layout(hovermode='x unified')
    
    # 2. Urgency distribution
    urgency_counts = filtered_df['Report_Urgency'].value_counts().reset_index()
    urgency_counts.columns = ['Urgency', 'Count']
    
    fig_urgency = px.bar(
        urgency_counts,
        x='Urgency',
        y='Count',
        title='Report Distribution by Urgency Level',
        labels={'Urgency': 'Urgency Level', 'Count': 'Number of Reports'},
        template='plotly_white',
        color='Count',
        color_continuous_scale='Blues'
    )
    
    # 3. Reliability pie chart
    reliability_counts = filtered_df['Reliability_Score'].value_counts().reset_index()
    reliability_counts.columns = ['Reliability', 'Count']
    
    fig_reliability_pie = px.pie(
        reliability_counts,
        values='Count',
        names='Reliability',
        title='Reliability Score Distribution',
        template='plotly_white',
        hole=0.4
    )
    
    # 4. Reliability bar chart
    fig_reliability_bar = px.bar(
        reliability_counts,
        x='Reliability',
        y='Count',
        title='Reports by Reliability Score',
        labels={'Reliability': 'Reliability Score', 'Count': 'Number of Reports'},
        template='plotly_white',
        color='Count',
        color_continuous_scale='Greens'
    )
    
    # 5. Geographic comparison
    geographic_data = pd.DataFrame({
        'Category': ['With Geographic Info', 'Without Geographic Info'],
        'Count': [
            filtered_df['Has_Geographic_Keywords'].sum(),
            len(filtered_df) - filtered_df['Has_Geographic_Keywords'].sum()
        ]
    })
    
    fig_geographic = px.bar(
        geographic_data,
        x='Category',
        y='Count',
        title='Reports with Geographic Keywords',
        labels={'Category': '', 'Count': 'Number of Reports'},
        template='plotly_white',
        color='Category',
        color_discrete_map={
            'With Geographic Info': color_scheme['success'],
            'Without Geographic Info': color_scheme['danger']
        }
    )
    
    # Calculate percentage
    if len(filtered_df) > 0:
        geo_pct = (filtered_df['Has_Geographic_Keywords'].sum() / len(filtered_df)) * 100
        fig_geographic.add_annotation(
            text=f"Coverage: {geo_pct:.1f}%",
            xref="paper", yref="paper",
            x=0.5, y=0.95,
            showarrow=False,
            font=dict(size=16, color=color_scheme['primary'])
        )
    
    # 6. Geographic keywords by sector
    sector_geo = filtered_df.groupby('Sector').agg({
        'Has_Geographic_Keywords': 'sum',
        'Report_ID': 'count'
    }).reset_index()
    sector_geo.columns = ['Sector', 'With_Geo', 'Total']
    sector_geo['Without_Geo'] = sector_geo['Total'] - sector_geo['With_Geo']
    
    fig_sector_geo = go.Figure(data=[
        go.Bar(name='With Geographic Info', x=sector_geo['Sector'], y=sector_geo['With_Geo'], 
               marker_color=color_scheme['success']),
        go.Bar(name='Without Geographic Info', x=sector_geo['Sector'], y=sector_geo['Without_Geo'],
               marker_color=color_scheme['danger'])
    ])
    fig_sector_geo.update_layout(
        barmode='stack',
        title='Geographic Information by Sector',
        xaxis_title='Sector',
        yaxis_title='Number of Reports',
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # 7. Data table
    table_data = filtered_df.head(100)[['Report_ID', 'Source_Date', 'Unit_Name', 'Sector', 
                                         'Report_Urgency', 'Reliability_Score', 'Content_Body']].copy()
    table_data['Content_Body'] = table_data['Content_Body'].str[:100] + '...'
    
    data_table = dash_table.DataTable(
        data=table_data.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in table_data.columns],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontFamily': 'Arial',
            'fontSize': '12px'
        },
        style_header={
            'backgroundColor': '#3498db',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f9f9f9'
            }
        ],
        page_size=10,
        sort_action='native',
        filter_action='native'
    )
    
    return fig_timeline, fig_urgency, fig_reliability_pie, fig_reliability_bar, fig_geographic, fig_sector_geo, data_table


# Run the app
if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Compass Intelligence Dashboard")
    print("="*60)
    print("\nDashboard features:")
    print("  1. Load Status: Report distribution by date and urgency")
    print("  2. Reliability Analysis: Distribution and metrics")
    print("  3. Intelligence Potential: Geographic keyword analysis")
    print("  4. Drill-down: Filters and interactive table")
    print("\nAccess the dashboard at: http://127.0.0.1:8050/")
    print("="*60 + "\n")
    
    app.run_server(debug=True, host='127.0.0.1', port=8050)

