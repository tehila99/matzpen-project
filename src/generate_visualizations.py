"""
Generate Static Visualizations
================================
This script generates static visualizations of the dashboard charts
and saves them as images for documentation purposes.

Author: Matzpen Project
Date: December 2025
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import os


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


def generate_visualizations():
    """Generate and save all visualizations."""
    
    print("\n" + "="*60)
    print("Generating Dashboard Visualizations")
    print("="*60)
    
    # Ensure output directory exists
    os.makedirs('outputs/visualizations', exist_ok=True)
    
    # Load data
    print("\nLoading data...")
    df = load_data()
    print(f"Loaded {len(df):,} reports")
    
    color_scheme = {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'success': '#2ca02c',
        'danger': '#d62728',
        'warning': '#ff7f0e',
        'info': '#17becf'
    }
    
    # 1. Reports over time
    print("\n1. Creating timeline chart...")
    reports_by_date = df.groupby('Date_Only').size().reset_index(name='Count')
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
    fig_timeline.write_image('outputs/visualizations/01_timeline.png', width=1200, height=600)
    print("   Saved: 01_timeline.png")
    
    # 2. Urgency distribution
    print("\n2. Creating urgency distribution chart...")
    urgency_counts = df['Report_Urgency'].value_counts().reset_index()
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
    fig_urgency.write_image('outputs/visualizations/02_urgency_distribution.png', width=1200, height=600)
    print("   Saved: 02_urgency_distribution.png")
    
    # 3. Reliability pie chart
    print("\n3. Creating reliability pie chart...")
    reliability_counts = df['Reliability_Score'].value_counts().reset_index()
    reliability_counts.columns = ['Reliability', 'Count']
    
    fig_reliability_pie = px.pie(
        reliability_counts,
        values='Count',
        names='Reliability',
        title='Reliability Score Distribution',
        template='plotly_white',
        hole=0.4
    )
    fig_reliability_pie.write_image('outputs/visualizations/03_reliability_pie.png', width=1200, height=600)
    print("   Saved: 03_reliability_pie.png")
    
    # 4. Reliability bar chart
    print("\n4. Creating reliability bar chart...")
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
    fig_reliability_bar.write_image('outputs/visualizations/04_reliability_bar.png', width=1200, height=600)
    print("   Saved: 04_reliability_bar.png")
    
    # 5. Geographic comparison
    print("\n5. Creating geographic comparison chart...")
    geographic_data = pd.DataFrame({
        'Category': ['With Geographic Info', 'Without Geographic Info'],
        'Count': [
            df['Has_Geographic_Keywords'].sum(),
            len(df) - df['Has_Geographic_Keywords'].sum()
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
    
    geo_pct = (df['Has_Geographic_Keywords'].sum() / len(df)) * 100
    fig_geographic.add_annotation(
        text=f"Coverage: {geo_pct:.1f}%",
        xref="paper", yref="paper",
        x=0.5, y=0.95,
        showarrow=False,
        font=dict(size=16, color=color_scheme['primary'])
    )
    fig_geographic.write_image('outputs/visualizations/05_geographic_comparison.png', width=1200, height=600)
    print("   Saved: 05_geographic_comparison.png")
    
    # 6. Geographic keywords by sector
    print("\n6. Creating sector geographic distribution chart...")
    sector_geo = df.groupby('Sector').agg({
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
    fig_sector_geo.write_image('outputs/visualizations/06_sector_geographic.png', width=1200, height=600)
    print("   Saved: 06_sector_geographic.png")
    
    # Summary statistics
    print("\n" + "="*60)
    print("Visualization Generation Complete")
    print("="*60)
    print(f"\nTotal visualizations created: 6")
    print(f"Location: outputs/visualizations/")
    print("\nGenerated files:")
    print("  - 01_timeline.png")
    print("  - 02_urgency_distribution.png")
    print("  - 03_reliability_pie.png")
    print("  - 04_reliability_bar.png")
    print("  - 05_geographic_comparison.png")
    print("  - 06_sector_geographic.png")


if __name__ == "__main__":
    try:
        generate_visualizations()
    except Exception as e:
        print(f"\nNote: To generate PNG images, install kaleido:")
        print("  pip install kaleido")
        print(f"\nError details: {e}")

