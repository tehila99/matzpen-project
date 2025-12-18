"""
Feature Engineering - Coordinate Extraction Engine
===================================================
שלב ג': מנוע חילוץ נ.צ (נקודות ציון) מתוך דיווחים מודיעיניים

This module extracts geographic coordinates from intelligence reports
using regex patterns with Hebrew anchor words.
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
import warnings
import sys
import io

warnings.filterwarnings('ignore')

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class CoordinateExtractor:
    """
    מנוע חילוץ נ.צ (נקודות ציון) מטקסט עברי
    
    האלגוריתם:
    1. חיפוש מילות עוגן: "נ.צ" / "נ.צ." / "נקודת ציון" / "מיקום"
    2. חילוץ 6 ספרות אחרי מילת העוגן (עם רווחים אפשריים)
    3. תיעוד כל החילוצים המוצלחים
    """
    
    def __init__(self):
        # רשימת דפוסי Regex לזיהוי נ.צ
        # Pattern explanation:
        # (?:נ\.צ\.?|נ\.צ|נקודת ציון|מיקום) - anchor words (non-capturing group)
        # \s* - optional whitespace
        # (\d{6}) - exactly 6 digits (captured group)
        self.patterns = [
            # דפוס 1: נ.צ עם או בלי נקודה אחרי + 6 ספרות
            r'נ\.צ\.?\s*(\d{6})',
            # דפוס 2: נקודת ציון + 6 ספרות
            r'נקודת\s+ציון\s*[:\s]*(\d{6})',
            # דפוס 3: מיקום + 6 ספרות
            r'מיקום\s*[:\s]*(\d{6})',
            # דפוס 4: נ.צ ללא נקודות + 6 ספרות
            r'נ\s*צ\s*[:\s]*(\d{6})',
            # דפוס 5: קואורדינטה / קוא + 6 ספרות
            r'קו[אר]*[דד]*ינט[הא]*\s*[:\s]*(\d{6})',
        ]
        
        self.stats = {
            'total_reports': 0,
            'reports_with_coordinates': 0,
            'reports_without_coordinates': 0,
            'extraction_rate': 0.0,
            'pattern_matches': {}
        }
    
    def extract_coordinate(self, text):
        """
        חילוץ נ.צ מטקסט בודד
        
        Args:
            text (str): תוכן הדיווח
            
        Returns:
            tuple: (coordinate_string, pattern_used)
                   או (None, None) אם לא נמצאה נ.צ
        """
        if pd.isna(text) or not isinstance(text, str):
            return None, None
        
        # ניסיון חילוץ עם כל הדפוסים
        for i, pattern in enumerate(self.patterns, 1):
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches:
                coordinate = matches.group(1)
                return coordinate, f"Pattern_{i}"
        
        return None, None
    
    def process_dataframe(self, df):
        """
        עיבוד DataFrame מלא - חילוץ נ.צ לכל הדיווחים
        
        Args:
            df (pd.DataFrame): DataFrame עם עמודת Content_Body
            
        Returns:
            pd.DataFrame: DataFrame מעודכן עם עמודות חדשות
        """
        print("Starting coordinate extraction...")
        print(f"Processing {len(df)} reports...")
        
        # אתחול עמודות חדשות
        df['Extracted_Coordinate'] = None
        df['Has_Coordinate'] = 0
        df['Extraction_Pattern'] = None
        
        # חילוץ נ.צ לכל שורה
        extraction_results = df['Content_Body'].apply(self.extract_coordinate)
        
        # הפרדת התוצאות
        df['Extracted_Coordinate'] = extraction_results.apply(lambda x: x[0])
        df['Extraction_Pattern'] = extraction_results.apply(lambda x: x[1])
        
        # עדכון דגל Has_Coordinate
        df['Has_Coordinate'] = df['Extracted_Coordinate'].notna().astype(int)
        
        # חישוב סטטיסטיקות
        self._calculate_statistics(df)
        
        return df
    
    def _calculate_statistics(self, df):
        """חישוב סטטיסטיקות על החילוץ"""
        self.stats['total_reports'] = len(df)
        self.stats['reports_with_coordinates'] = df['Has_Coordinate'].sum()
        self.stats['reports_without_coordinates'] = len(df) - self.stats['reports_with_coordinates']
        
        if self.stats['total_reports'] > 0:
            self.stats['extraction_rate'] = (
                self.stats['reports_with_coordinates'] / self.stats['total_reports'] * 100
            )
        
        # ספירת התאמות לפי דפוס
        pattern_counts = df[df['Extraction_Pattern'].notna()]['Extraction_Pattern'].value_counts()
        self.stats['pattern_matches'] = pattern_counts.to_dict()
    
    def generate_quality_report(self, df, output_path):
        """
        יצירת דוח בקרת איכות על תהליך החילוץ
        
        Args:
            df (pd.DataFrame): DataFrame מעובד
            output_path (str): נתיב לשמירת הדוח
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("COORDINATE EXTRACTION - QUALITY CONTROL REPORT")
        report_lines.append("דוח בקרת איכות - חילוץ נ.צ (נקודות ציון)")
        report_lines.append("=" * 80)
        report_lines.append(f"\nGeneration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Input File: data/processed/clean_reports.csv")
        report_lines.append(f"Output File: data/processed/reports_with_coordinates.csv")
        report_lines.append("\n")
        
        # סטטיסטיקות כלליות
        report_lines.append("-" * 80)
        report_lines.append("OVERALL STATISTICS")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Reports Processed: {self.stats['total_reports']:,}")
        report_lines.append(f"Reports with Coordinates Found: {self.stats['reports_with_coordinates']:,}")
        report_lines.append(f"Reports without Coordinates: {self.stats['reports_without_coordinates']:,}")
        report_lines.append(f"Extraction Success Rate: {self.stats['extraction_rate']:.2f}%")
        report_lines.append("\n")
        
        # פילוח לפי דפוס חילוץ
        report_lines.append("-" * 80)
        report_lines.append("EXTRACTION PATTERN BREAKDOWN")
        report_lines.append("-" * 80)
        for pattern, count in sorted(self.stats['pattern_matches'].items()):
            percentage = (count / self.stats['reports_with_coordinates'] * 100) if self.stats['reports_with_coordinates'] > 0 else 0
            report_lines.append(f"{pattern}: {count:,} matches ({percentage:.1f}%)")
        report_lines.append("\n")
        
        # דוגמאות מוצלחות
        report_lines.append("-" * 80)
        report_lines.append("SUCCESSFUL EXTRACTION EXAMPLES (First 10)")
        report_lines.append("-" * 80)
        successful = df[df['Has_Coordinate'] == 1].head(10)
        for idx, row in successful.iterrows():
            report_lines.append(f"\nReport ID: {row['Report_ID']}")
            report_lines.append(f"Extracted Coordinate: {row['Extracted_Coordinate']}")
            report_lines.append(f"Pattern Used: {row['Extraction_Pattern']}")
            report_lines.append(f"Content Preview: {row['Content_Body'][:100]}...")
            report_lines.append("-" * 40)
        
        # דוגמאות לא מוצלחות
        report_lines.append("\n")
        report_lines.append("-" * 80)
        report_lines.append("UNSUCCESSFUL EXTRACTION EXAMPLES (First 10)")
        report_lines.append("-" * 80)
        unsuccessful = df[df['Has_Coordinate'] == 0].head(10)
        for idx, row in unsuccessful.iterrows():
            report_lines.append(f"\nReport ID: {row['Report_ID']}")
            report_lines.append(f"Content: {row['Content_Body'][:150]}...")
            report_lines.append("-" * 40)
        
        # פילוח לפי גזרה
        report_lines.append("\n")
        report_lines.append("-" * 80)
        report_lines.append("EXTRACTION RATE BY SECTOR")
        report_lines.append("-" * 80)
        sector_analysis = df.groupby('Sector').agg({
            'Has_Coordinate': ['sum', 'count']
        }).round(2)
        sector_analysis.columns = ['With_Coordinates', 'Total_Reports']
        sector_analysis['Extraction_Rate_%'] = (
            sector_analysis['With_Coordinates'] / sector_analysis['Total_Reports'] * 100
        ).round(2)
        sector_analysis = sector_analysis.sort_values('Extraction_Rate_%', ascending=False)
        
        report_lines.append(f"\n{'Sector':<30} {'With Coords':<15} {'Total':<15} {'Rate %':<10}")
        report_lines.append("-" * 70)
        for sector, row in sector_analysis.iterrows():
            report_lines.append(
                f"{sector:<30} {int(row['With_Coordinates']):<15} "
                f"{int(row['Total_Reports']):<15} {row['Extraction_Rate_%']:<10.2f}"
            )
        
        # פילוח לפי דחיפות
        report_lines.append("\n")
        report_lines.append("-" * 80)
        report_lines.append("EXTRACTION RATE BY URGENCY")
        report_lines.append("-" * 80)
        urgency_analysis = df.groupby('Report_Urgency').agg({
            'Has_Coordinate': ['sum', 'count']
        }).round(2)
        urgency_analysis.columns = ['With_Coordinates', 'Total_Reports']
        urgency_analysis['Extraction_Rate_%'] = (
            urgency_analysis['With_Coordinates'] / urgency_analysis['Total_Reports'] * 100
        ).round(2)
        urgency_analysis = urgency_analysis.sort_values('Extraction_Rate_%', ascending=False)
        
        report_lines.append(f"\n{'Urgency':<30} {'With Coords':<15} {'Total':<15} {'Rate %':<10}")
        report_lines.append("-" * 70)
        for urgency, row in urgency_analysis.iterrows():
            report_lines.append(
                f"{urgency:<30} {int(row['With_Coordinates']):<15} "
                f"{int(row['Total_Reports']):<15} {row['Extraction_Rate_%']:<10.2f}"
            )
        
        # המלצות
        report_lines.append("\n")
        report_lines.append("-" * 80)
        report_lines.append("RECOMMENDATIONS FOR IMPROVEMENT")
        report_lines.append("-" * 80)
        
        if self.stats['extraction_rate'] < 20:
            report_lines.append("• Low extraction rate detected. Consider adding more regex patterns.")
        if self.stats['extraction_rate'] > 50:
            report_lines.append("• Good extraction rate! Model is performing well.")
        
        report_lines.append("• Review unsuccessful examples to identify missed patterns")
        report_lines.append("• Consider manual tagging of sample to validate accuracy")
        report_lines.append("• Monitor extraction rates by sector for potential biases")
        
        report_lines.append("\n")
        report_lines.append("=" * 80)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 80)
        
        # שמירת הדוח
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"\n[OK] Quality control report saved to: {output_path}")


def main():
    """
    Main execution function
    """
    print("=" * 80)
    print("FEATURE ENGINEERING - COORDINATE EXTRACTION")
    print("שלב ג': חילוץ נ.צ (נקודות ציון)")
    print("=" * 80)
    print()
    
    # הגדרת נתיבים
    input_file = Path('data/processed/clean_reports.csv')
    output_file = Path('data/processed/reports_with_coordinates.csv')
    report_file = Path('outputs/reports/feature_engineering_report.txt')
    
    # בדיקת קיום קובץ קלט
    if not input_file.exists():
        print(f"[ERROR] Input file not found at {input_file}")
        print("Please run data cleansing (step 1) first.")
        return
    
    # טעינת הנתונים
    print(f"Loading data from: {input_file}")
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
        print(f"[OK] Loaded {len(df):,} reports successfully")
    except Exception as e:
        print(f"[ERROR] Error loading data: {e}")
        return
    
    print()
    
    # יצירת מנוע החילוץ
    extractor = CoordinateExtractor()
    
    # עיבוד הדיווחים
    print("Processing reports for coordinate extraction...")
    df_processed = extractor.process_dataframe(df)
    print("[OK] Extraction completed")
    print()
    
    # הצגת תוצאות
    print("-" * 80)
    print("EXTRACTION RESULTS")
    print("-" * 80)
    print(f"Total Reports: {extractor.stats['total_reports']:,}")
    print(f"Coordinates Found: {extractor.stats['reports_with_coordinates']:,}")
    print(f"No Coordinates: {extractor.stats['reports_without_coordinates']:,}")
    print(f"Success Rate: {extractor.stats['extraction_rate']:.2f}%")
    print()
    
    # שמירת הנתונים
    print(f"Saving processed data to: {output_file}")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_processed.to_csv(output_file, index=False, encoding='utf-8')
    print("[OK] Data saved successfully")
    print()
    
    # יצירת דוח בקרת איכות
    print("Generating quality control report...")
    extractor.generate_quality_report(df_processed, report_file)
    print()
    
    print("=" * 80)
    print("FEATURE ENGINEERING COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("Output Files:")
    print(f"  1. Processed Data: {output_file}")
    print(f"  2. Quality Report: {report_file}")
    print()
    print("Next Step: Review the quality report and proceed to Step 4 (Tagging)")


if __name__ == "__main__":
    main()

