"""
Quick analysis: Sector vs Reliability for errors
"""
import pandas as pd

# Load data
df = pd.read_csv('data/tagging/דאטה מתויג לתהילה.csv', encoding='utf-8-sig')

# Clean
df['Y_N_MODEL'] = df['Y_N_MODEL'].astype(str).str.strip().str.upper()
df['Y_N_TAG'] = df['Y_N_TAG'].astype(str).str.strip().str.upper()

# Mark errors
df['Error'] = ((df['Y_N_MODEL'] == 'YES') & (df['Y_N_TAG'] == 'NO')) | \
              ((df['Y_N_MODEL'] == 'NO') & (df['Y_N_TAG'] == 'YES'))

print("="*80)
print("SECTOR vs RELIABILITY - ERROR ANALYSIS")
print("="*80)

# Get errors only
errors_df = df[df['Error'] == True]
print(f"\nTotal errors: {len(errors_df)}")

# Crosstab of errors
print("\n" + "="*80)
print("ERRORS by Sector and Reliability:")
print("="*80)
error_crosstab = pd.crosstab(errors_df['Sector'], errors_df['Reliability_Score'], margins=True)
print(error_crosstab)

# Worst sector analysis
print("\n" + "="*80)
print("WORST SECTOR ANALYSIS: חטיבת שומרון")
print("="*80)

worst_sector = 'חטיבת שומרון'
sector_df = df[df['Sector'] == worst_sector]
sector_errors = sector_df[sector_df['Error'] == True]

print(f"\nTotal reports in {worst_sector}: {len(sector_df)}")
print(f"Total errors: {len(sector_errors)}")
print(f"\nReliability distribution in errors:")

for rel in sorted(sector_errors['Reliability_Score'].unique()):
    count = len(sector_errors[sector_errors['Reliability_Score'] == rel])
    print(f"  {rel}: {count} errors")

# Compare to other sectors
print("\n" + "="*80)
print("ERRORS BY SECTOR - WITH RELIABILITY BREAKDOWN")
print("="*80)

for sector in sorted(df['Sector'].unique()):
    sector_df_full = df[df['Sector'] == sector]
    sector_errors_full = sector_df_full[sector_df_full['Error'] == True]
    
    if len(sector_errors_full) > 0:
        print(f"\n{sector}: {len(sector_errors_full)} errors")
        rel_dist = sector_errors_full['Reliability_Score'].value_counts()
        for rel, count in rel_dist.items():
            print(f"  - {rel}: {count}")

# Overall reliability in sample
print("\n" + "="*80)
print("OVERALL RELIABILITY DISTRIBUTION")
print("="*80)
print("\nAll 100 reports:")
print(df['Reliability_Score'].value_counts().sort_index())

print("\nOnly errors (11 total):")
print(errors_df['Reliability_Score'].value_counts().sort_index())

# Conclusion
print("\n" + "="*80)
print("CONCLUSION: Is there a connection?")
print("="*80)

d4_total = len(df[df['Reliability_Score'].str.contains('D4', na=False)])
d4_errors = len(errors_df[errors_df['Reliability_Score'].str.contains('D4', na=False)])
d4_error_rate = d4_errors / d4_total if d4_total > 0 else 0

other_total = len(df[~df['Reliability_Score'].str.contains('D4', na=False)])
other_errors = len(errors_df[~errors_df['Reliability_Score'].str.contains('D4', na=False)])
other_error_rate = other_errors / other_total if other_total > 0 else 0

print(f"\nD4 reports: {d4_total} total, {d4_errors} errors ({d4_error_rate:.1%} error rate)")
print(f"Non-D4 reports: {other_total} total, {other_errors} errors ({other_error_rate:.1%} error rate)")

print("\nAnswer: ", end="")
if abs(d4_error_rate - other_error_rate) < 0.05:
    print("NO significant connection between reliability and errors!")
else:
    print("YES - there is a connection!")

print("\n" + "="*80)

