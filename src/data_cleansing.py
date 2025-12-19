"""
Data Cleansing Script - Stage A
================================
This script cleans and filters the raw intelligence reports data.

Filtering Logic:
1. Remove rows without Report_ID or with empty Report_ID
2. Remove rows with Content_Body shorter than 5 characters
3. Filter out reports with Reliability_Score 'F' (unreliable)
4. Save cleaned data to CSV
5. Generate a detailed cleansing report

Author: Matzpen Project
Date: December 2025
"""

import pandas as pd
import os
from datetime import datetime


def load_raw_data(file_path):
    """
    Load raw mission data from CSV file.
    
    Args:
        file_path (str): Path to the raw data CSV file
        
    Returns:
        pd.DataFrame: Raw data as DataFrame
    """
    print(f"Loading data from: {file_path}")
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
    return df


def clean_data(df):
    """
    Clean the data according to the filtering logic.
    
    Args:
        df (pd.DataFrame): Raw data
        
    Returns:
        tuple: (cleaned_df, cleansing_stats)
    """
    # Track statistics for the report
    stats = {
        'initial_count': len(df),
        'removed_no_report_id': 0,
        'removed_short_content': 0,
        'removed_unreliable': 0,
        'final_count': 0
    }
    
    print("\n" + "="*60)
    print("Starting Data Cleansing Process")
    print("="*60)
    
    # Step 1: Remove rows without Report_ID or with empty Report_ID
    print("\nStep 1: Removing rows without Report_ID...")
    print(f"  Initial rows: {len(df)}")
    print(f"  Rows with null Report_ID: {df['Report_ID'].isnull().sum()}")
    
    df_step1 = df[df['Report_ID'].notna()].copy()
    stats['removed_no_report_id'] = len(df) - len(df_step1)
    
    print(f"  Removed: {stats['removed_no_report_id']} rows")
    print(f"  Remaining: {len(df_step1)} rows")
    
    # Step 2: Remove rows with Content_Body shorter than 5 characters or null
    print("\nStep 2: Removing rows with short or empty Content_Body...")
    print(f"  Rows with null Content_Body: {df_step1['Content_Body'].isnull().sum()}")
    
    # First, handle null values
    df_step2 = df_step1[df_step1['Content_Body'].notna()].copy()
    
    # Then, filter by length (minimum 5 characters)
    df_step2 = df_step2[df_step2['Content_Body'].str.len() >= 5].copy()
    
    stats['removed_short_content'] = len(df_step1) - len(df_step2)
    print(f"  Removed: {stats['removed_short_content']} rows")
    print(f"  Remaining: {len(df_step2)} rows")
    
    # Step 3: Filter out reports with Reliability_Score 'F' (unreliable)
    print("\nStep 3: Filtering out unreliable reports (Reliability_Score = F)...")
    print(f"  Reliability Score distribution before filtering:")
    print(df_step2['Reliability_Score'].value_counts())
    
    # Filter out rows where Reliability_Score contains 'F'
    df_step3 = df_step2[~df_step2['Reliability_Score'].str.contains('F', na=False, case=False)].copy()
    
    stats['removed_unreliable'] = len(df_step2) - len(df_step3)
    print(f"\n  Removed: {stats['removed_unreliable']} rows with reliability 'F'")
    print(f"  Remaining: {len(df_step3)} rows")
    
    # Final statistics
    stats['final_count'] = len(df_step3)
    
    print("\n" + "="*60)
    print("Data Cleansing Complete")
    print("="*60)
    print(f"Initial rows: {stats['initial_count']}")
    print(f"Final rows: {stats['final_count']}")
    print(f"Total removed: {stats['initial_count'] - stats['final_count']}")
    print(f"Retention rate: {(stats['final_count'] / stats['initial_count'] * 100):.2f}%")
    
    return df_step3, stats


def save_cleaned_data(df, output_path):
    """
    Save cleaned data to CSV file.
    
    Args:
        df (pd.DataFrame): Cleaned data
        output_path (str): Path to save the cleaned data
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\nCleaned data saved to: {output_path}")


def generate_report(stats, df_clean, output_path):
    """
    Generate a detailed cleansing report.
    
    Args:
        stats (dict): Cleansing statistics
        df_clean (pd.DataFrame): Cleaned data
        output_path (str): Path to save the report
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("DATA CLEANSING REPORT - MATZPEN PROJECT")
    report_lines.append("=" * 80)
    report_lines.append(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("\n")
    
    # Summary Statistics
    report_lines.append("-" * 80)
    report_lines.append("SUMMARY STATISTICS")
    report_lines.append("-" * 80)
    report_lines.append(f"Initial row count:                {stats['initial_count']:,}")
    report_lines.append(f"Rows removed (no Report_ID):      {stats['removed_no_report_id']:,}")
    report_lines.append(f"Rows removed (short content):     {stats['removed_short_content']:,}")
    report_lines.append(f"Rows removed (unreliable F):      {stats['removed_unreliable']:,}")
    report_lines.append(f"Final row count:                  {stats['final_count']:,}")
    report_lines.append(f"Total rows removed:               {stats['initial_count'] - stats['final_count']:,}")
    report_lines.append(f"Retention rate:                   {(stats['final_count'] / stats['initial_count'] * 100):.2f}%")
    report_lines.append("\n")
    
    # Cleansing Logic Description
    report_lines.append("-" * 80)
    report_lines.append("CLEANSING LOGIC APPLIED")
    report_lines.append("-" * 80)
    report_lines.append("1. Removed rows without Report_ID or with empty Report_ID")
    report_lines.append("   - Rationale: Report_ID is a critical identifier for tracking reports")
    report_lines.append(f"   - Impact: {stats['removed_no_report_id']} rows removed")
    report_lines.append("\n")
    report_lines.append("2. Removed rows with Content_Body shorter than 5 characters")
    report_lines.append("   - Rationale: Very short content lacks sufficient information")
    report_lines.append(f"   - Impact: {stats['removed_short_content']} rows removed")
    report_lines.append("\n")
    report_lines.append("3. Filtered out reports with Reliability_Score 'F' (unreliable)")
    report_lines.append("   - Rationale: Unreliable reports may contain inaccurate information")
    report_lines.append(f"   - Impact: {stats['removed_unreliable']} rows removed")
    report_lines.append("\n")
    
    # Data Quality Metrics
    report_lines.append("-" * 80)
    report_lines.append("CLEANED DATA QUALITY METRICS")
    report_lines.append("-" * 80)
    report_lines.append(f"Total reports in cleaned dataset: {len(df_clean):,}")
    report_lines.append(f"\nNull values per column:")
    for col in df_clean.columns:
        null_count = df_clean[col].isnull().sum()
        null_pct = (null_count / len(df_clean) * 100) if len(df_clean) > 0 else 0
        report_lines.append(f"  {col:25s}: {null_count:5d} ({null_pct:5.2f}%)")
    
    # Distribution of key fields
    report_lines.append(f"\n")
    report_lines.append("-" * 80)
    report_lines.append("KEY FIELD DISTRIBUTIONS")
    report_lines.append("-" * 80)
    
    # Reliability Score distribution
    report_lines.append("\nReliability Score Distribution:")
    reliability_dist = df_clean['Reliability_Score'].value_counts()
    for score, count in reliability_dist.items():
        pct = (count / len(df_clean) * 100) if len(df_clean) > 0 else 0
        report_lines.append(f"  {score:25s}: {count:5d} ({pct:5.2f}%)")
    
    # Report Urgency distribution
    report_lines.append("\nReport Urgency Distribution:")
    urgency_dist = df_clean['Report_Urgency'].value_counts()
    for urgency, count in urgency_dist.items():
        pct = (count / len(df_clean) * 100) if len(df_clean) > 0 else 0
        report_lines.append(f"  {urgency:25s}: {count:5d} ({pct:5.2f}%)")
    
    # Sector distribution
    report_lines.append("\nSector Distribution:")
    sector_dist = df_clean['Sector'].value_counts()
    for sector, count in sector_dist.items():
        pct = (count / len(df_clean) * 100) if len(df_clean) > 0 else 0
        report_lines.append(f"  {sector:25s}: {count:5d} ({pct:5.2f}%)")
    
    # Content length statistics
    report_lines.append("\nContent Body Length Statistics:")
    content_lengths = df_clean['Content_Body'].str.len()
    report_lines.append(f"  Minimum length:  {content_lengths.min():.0f} characters")
    report_lines.append(f"  Maximum length:  {content_lengths.max():.0f} characters")
    report_lines.append(f"  Mean length:     {content_lengths.mean():.2f} characters")
    report_lines.append(f"  Median length:   {content_lengths.median():.0f} characters")
    
    # Sample data
    report_lines.append("\n")
    report_lines.append("-" * 80)
    report_lines.append("SAMPLE DATA (First 5 rows)")
    report_lines.append("-" * 80)
    report_lines.append("\n")
    
    for idx, row in df_clean.head(5).iterrows():
        report_lines.append(f"Report ID: {row['Report_ID']}")
        report_lines.append(f"  Date: {row['Source_Date']}")
        report_lines.append(f"  Unit: {row['Unit_Name']}")
        report_lines.append(f"  Sector: {row['Sector']}")
        report_lines.append(f"  Urgency: {row['Report_Urgency']}")
        report_lines.append(f"  Reliability: {row['Reliability_Score']}")
        report_lines.append(f"  Content: {row['Content_Body'][:100]}...")
        report_lines.append("\n")
    
    report_lines.append("=" * 80)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 80)
    
    # Write report to file
    report_text = "\n".join(report_lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"\nDetailed report saved to: {output_path}")


def main():
    """Main execution function."""
    # Define file paths
    raw_data_path = 'data/raw/raw_mission_data_final.csv'
    clean_data_path = 'data/processed/clean_reports.csv'
    report_path = 'outputs/reports/data_cleansing_report.txt'
    
    # Load raw data
    df_raw = load_raw_data(raw_data_path)
    
    # Clean data
    df_clean, stats = clean_data(df_raw)
    
    # Save cleaned data
    save_cleaned_data(df_clean, clean_data_path)
    
    # Generate report
    generate_report(stats, df_clean, report_path)
    
    print("\n" + "="*60)
    print("Data cleansing process completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()

