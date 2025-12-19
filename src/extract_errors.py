"""
Extract all 11 errors from the tagged data and create a focused CSV file
for manual inspection and analysis.

Author: Project Matzpen
Date: December 2025
"""

import sys
import io
import pandas as pd
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def extract_errors():
    """
    חילוץ כל 11 השגיאות מהקובץ המתוייג
    יצירת קובץ CSV ממוקד לבדיקה ידנית
    """
    print("=" * 80)
    print("EXTRACTING ERRORS FROM TAGGED DATA")
    print("חילוץ שגיאות מהנתונים המתוייגים")
    print("=" * 80)
    
    # Load tagged data
    tagged_file = Path('data/tagging/דאטה מתויג לתהילה.csv')
    print(f"\nLoading: {tagged_file}")
    
    df = pd.read_csv(tagged_file, encoding='utf-8-sig')
    print(f"✓ Loaded {len(df)} records")
    
    # Identify errors
    # False Positives: Model said YES, but Tag said NO
    fp_mask = (df['Y_N_MODEL'].str.upper() == 'YES') & (df['Y_N_TAG'].str.upper() == 'NO')
    
    # False Negatives: Model said NO, but Tag said YES
    fn_mask = (df['Y_N_MODEL'].str.upper() == 'NO') & (df['Y_N_TAG'].str.upper() == 'YES')
    
    # Get all errors
    errors_df = df[fp_mask | fn_mask].copy()
    
    print(f"\n📊 Found {len(errors_df)} errors:")
    print(f"   - False Positives (FP): {fp_mask.sum()}")
    print(f"   - False Negatives (FN): {fn_mask.sum()}")
    
    # Add error type column
    errors_df['Error_Type'] = errors_df.apply(
        lambda row: 'FP' if row['Y_N_MODEL'].upper() == 'YES' and row['Y_N_TAG'].upper() == 'NO' else 'FN',
        axis=1
    )
    
    # Sort by Reliability_Score, then by Sector
    errors_df = errors_df.sort_values(by=['Reliability_Score', 'Sector'], ascending=[True, True])
    
    # Reorder columns to put Error_Type first for easy viewing
    columns_order = ['Error_Type', 'Report_ID', 'Content_Body', 'Extracted_Coordinate', 
                     'Y_N_MODEL', 'Y_N_TAG', 'Tagged_Coordinate', 'Is_Edge_Case', 
                     'Sector', 'Report_Urgency', 'Reliability_Score']
    
    errors_df = errors_df[columns_order]
    
    # Save to CSV
    output_dir = Path('outputs/reports')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'errors_analysis_11_cases.csv'
    
    errors_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ Saved to: {output_file}")
    
    # Print summary by reliability and sector
    print("\n" + "=" * 80)
    print("ERRORS BREAKDOWN")
    print("=" * 80)
    
    print("\nBy Reliability Score:")
    print("-" * 40)
    for rel in sorted(errors_df['Reliability_Score'].unique()):
        rel_errors = errors_df[errors_df['Reliability_Score'] == rel]
        fp_count = len(rel_errors[rel_errors['Error_Type'] == 'FP'])
        fn_count = len(rel_errors[rel_errors['Error_Type'] == 'FN'])
        print(f"  {rel}: {len(rel_errors)} errors ({fp_count} FP, {fn_count} FN)")
    
    print("\nBy Sector:")
    print("-" * 40)
    for sector in sorted(errors_df['Sector'].unique()):
        sector_errors = errors_df[errors_df['Sector'] == sector]
        fp_count = len(sector_errors[sector_errors['Error_Type'] == 'FP'])
        fn_count = len(sector_errors[sector_errors['Error_Type'] == 'FN'])
        print(f"  {sector}: {len(sector_errors)} errors ({fp_count} FP, {fn_count} FN)")
    
    print("\n" + "=" * 80)
    print("✅ ALL ERRORS EXTRACTED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nOpen the file to inspect all 11 errors in detail:")
    print(f"📄 {output_file}")
    print()

if __name__ == '__main__':
    extract_errors()

