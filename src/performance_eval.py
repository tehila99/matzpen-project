"""
Performance Evaluation - Model Assessment
==========================================
שלב ה': הערכת ביצועים של מודל חילוץ נ.צ

This module evaluates the coordinate extraction model by comparing
its predictions against human-tagged ground truth.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter
import warnings
import sys
import io

warnings.filterwarnings('ignore')

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class PerformanceEvaluator:
    """
    מעריך ביצועים - מחשב מדדי דיוק של המודל
    
    מטריקות:
    - Confusion Matrix (TP, FP, TN, FN)
    - Precision, Recall, F1-Score, Accuracy
    - Error analysis by Sector and Reliability
    """
    
    def __init__(self, tagged_file_path):
        """
        אתחול המעריך
        
        Args:
            tagged_file_path: נתיב לקובץ המתוייג
        """
        self.tagged_file = Path(tagged_file_path)
        self.df = None
        self.confusion_matrix = {}
        self.metrics = {}
        self.errors = {'false_positives': [], 'false_negatives': []}
        
        print("="*80)
        print("PERFORMANCE EVALUATION - STEP 5")
        print("הערכת ביצועים - שלב ה'")
        print("="*80)
        print()
    
    def load_tagged_data(self):
        """
        טעינת הנתונים המתוייגים
        """
        print(f"Loading tagged data from: {self.tagged_file}")
        
        if not self.tagged_file.exists():
            raise FileNotFoundError(f"Tagged file not found: {self.tagged_file}")
        
        # Try different encodings for Hebrew support
        encodings = ['utf-8-sig', 'utf-8', 'cp1255', 'iso-8859-8']
        
        for encoding in encodings:
            try:
                self.df = pd.read_csv(self.tagged_file, encoding=encoding)
                print(f"✓ File loaded successfully with encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if self.df is None:
            raise ValueError("Could not load file with any encoding")
        
        print(f"Total records loaded: {len(self.df)}")
        print()
        
        # Validate required columns
        required_cols = ['Y_N_MODEL', 'Y_N_TAG']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Clean and standardize Y_N columns
        self.df['Y_N_MODEL'] = self.df['Y_N_MODEL'].astype(str).str.strip().str.upper()
        self.df['Y_N_TAG'] = self.df['Y_N_TAG'].astype(str).str.strip().str.upper()
        
        # Validate values
        valid_values = ['YES', 'NO']
        invalid_model = self.df[~self.df['Y_N_MODEL'].isin(valid_values)]
        invalid_tag = self.df[~self.df['Y_N_TAG'].isin(valid_values)]
        
        if len(invalid_model) > 0:
            print(f"⚠️ Warning: {len(invalid_model)} records with invalid Y_N_MODEL values")
            print(f"   Invalid values: {invalid_model['Y_N_MODEL'].unique()}")
        
        if len(invalid_tag) > 0:
            print(f"⚠️ Warning: {len(invalid_tag)} records with invalid Y_N_TAG values")
            print(f"   Invalid values: {invalid_tag['Y_N_TAG'].unique()}")
            print()
        
        # Filter to valid records only
        self.df = self.df[
            (self.df['Y_N_MODEL'].isin(valid_values)) & 
            (self.df['Y_N_TAG'].isin(valid_values))
        ].copy()
        
        print(f"Valid records for evaluation: {len(self.df)}")
        print()
    
    def calculate_confusion_matrix(self):
        """
        חישוב מטריצת בילבול (Confusion Matrix)
        
        TP (True Positive): Model=Yes, Tag=Yes ✓
        FP (False Positive): Model=Yes, Tag=No ✗
        TN (True Negative): Model=No, Tag=No ✓
        FN (False Negative): Model=No, Tag=Yes ✗
        """
        print("Calculating Confusion Matrix...")
        print("-" * 80)
        
        tp = len(self.df[(self.df['Y_N_MODEL'] == 'YES') & (self.df['Y_N_TAG'] == 'YES')])
        fp = len(self.df[(self.df['Y_N_MODEL'] == 'YES') & (self.df['Y_N_TAG'] == 'NO')])
        tn = len(self.df[(self.df['Y_N_MODEL'] == 'NO') & (self.df['Y_N_TAG'] == 'NO')])
        fn = len(self.df[(self.df['Y_N_MODEL'] == 'NO') & (self.df['Y_N_TAG'] == 'YES')])
        
        self.confusion_matrix = {
            'TP': tp,  # True Positives
            'FP': fp,  # False Positives
            'TN': tn,  # True Negatives
            'FN': fn   # False Negatives
        }
        
        # Store error cases for analysis
        self.errors['false_positives'] = self.df[
            (self.df['Y_N_MODEL'] == 'YES') & (self.df['Y_N_TAG'] == 'NO')
        ].copy()
        
        self.errors['false_negatives'] = self.df[
            (self.df['Y_N_MODEL'] == 'NO') & (self.df['Y_N_TAG'] == 'YES')
        ].copy()
        
        # Print confusion matrix
        print("\nConfusion Matrix:")
        print("                     Actual (Human Tag)")
        print("                     Positive    Negative")
        print(f"Predicted    Positive    {tp:4d}        {fp:4d}     (Model said YES)")
        print(f"(Model)      Negative    {fn:4d}        {tn:4d}     (Model said NO)")
        print()
        print(f"TP (True Positive):  {tp:4d} - Model correctly identified coordinates")
        print(f"FP (False Positive): {fp:4d} - Model incorrectly extracted non-coordinates")
        print(f"TN (True Negative):  {tn:4d} - Model correctly identified no coordinates")
        print(f"FN (False Negative): {fn:4d} - Model missed actual coordinates")
        print()
    
    def calculate_metrics(self):
        """
        חישוב מדדי ביצועים
        
        Precision = TP / (TP + FP) - מתוך מה שאמרנו "כן", כמה נכון?
        Recall = TP / (TP + FN) - מתוך כל ה"כן" האמיתיים, כמה תפסנו?
        F1-Score = 2 * (Precision * Recall) / (Precision + Recall)
        Accuracy = (TP + TN) / Total - אחוז הצלחה כללי
        """
        print("Calculating Performance Metrics...")
        print("-" * 80)
        
        tp = self.confusion_matrix['TP']
        fp = self.confusion_matrix['FP']
        tn = self.confusion_matrix['TN']
        fn = self.confusion_matrix['FN']
        
        total = tp + fp + tn + fn
        
        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = (tp + tn) / total if total > 0 else 0
        
        # Specificity (True Negative Rate)
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        self.metrics = {
            'Precision': precision,
            'Recall': recall,
            'F1-Score': f1_score,
            'Accuracy': accuracy,
            'Specificity': specificity
        }
        
        # Print metrics
        print("\n📊 Performance Metrics:")
        print("=" * 80)
        print(f"Precision:    {precision:.2%}  - Of all 'Yes' predictions, how many were correct?")
        print(f"              → {tp} correct out of {tp + fp} predictions")
        print()
        print(f"Recall:       {recall:.2%}  - Of all actual coordinates, how many did we catch?")
        print(f"              → {tp} caught out of {tp + fn} actual")
        print()
        print(f"F1-Score:     {f1_score:.2%}  - Harmonic mean of Precision & Recall")
        print()
        print(f"Accuracy:     {accuracy:.2%}  - Overall correctness")
        print(f"              → {tp + tn} correct out of {total} total")
        print()
        print(f"Specificity:  {specificity:.2%}  - Of all actual negatives, how many identified?")
        print(f"              → {tn} correct out of {tn + fp} actual negatives")
        print()
    
    def analyze_errors_by_sector(self):
        """
        ניתוח שגיאות לפי מגזר (Sector)
        """
        print("\n📍 Error Analysis by Sector (גזרה):")
        print("=" * 80)
        
        if 'Sector' not in self.df.columns:
            print("⚠️ Sector column not found - skipping sector analysis")
            return
        
        sectors = self.df['Sector'].unique()
        
        print(f"\n{'Sector':<25} {'Total':>8} {'TP':>6} {'FP':>6} {'TN':>6} {'FN':>6} {'Accuracy':>10}")
        print("-" * 80)
        
        for sector in sorted(sectors):
            sector_df = self.df[self.df['Sector'] == sector]
            
            tp = len(sector_df[(sector_df['Y_N_MODEL'] == 'YES') & (sector_df['Y_N_TAG'] == 'YES')])
            fp = len(sector_df[(sector_df['Y_N_MODEL'] == 'YES') & (sector_df['Y_N_TAG'] == 'NO')])
            tn = len(sector_df[(sector_df['Y_N_MODEL'] == 'NO') & (sector_df['Y_N_TAG'] == 'NO')])
            fn = len(sector_df[(sector_df['Y_N_MODEL'] == 'NO') & (sector_df['Y_N_TAG'] == 'YES')])
            
            total = len(sector_df)
            accuracy = (tp + tn) / total if total > 0 else 0
            
            print(f"{sector:<25} {total:>8} {tp:>6} {fp:>6} {tn:>6} {fn:>6} {accuracy:>9.1%}")
        
        print()
        
        # Identify worst performing sector
        if len(sectors) > 0:
            sector_errors = []
            for sector in sectors:
                sector_df = self.df[self.df['Sector'] == sector]
                fp = len(sector_df[(sector_df['Y_N_MODEL'] == 'YES') & (sector_df['Y_N_TAG'] == 'NO')])
                fn = len(sector_df[(sector_df['Y_N_MODEL'] == 'NO') & (sector_df['Y_N_TAG'] == 'YES')])
                sector_errors.append((sector, fp + fn))
            
            sector_errors.sort(key=lambda x: x[1], reverse=True)
            worst_sector = sector_errors[0]
            
            if worst_sector[1] > 0:
                print(f"⚠️ Sector with most errors: {worst_sector[0]} ({worst_sector[1]} errors)")
            print()
    
    def analyze_errors_by_reliability(self):
        """
        ניתוח שגיאות לפי ציון אמינות
        """
        print("\n🔍 Error Analysis by Reliability Score (אמינות):")
        print("=" * 80)
        
        if 'Reliability_Score' not in self.df.columns:
            print("⚠️ Reliability_Score column not found - skipping reliability analysis")
            return
        
        reliabilities = self.df['Reliability_Score'].unique()
        
        print(f"\n{'Reliability':<30} {'Total':>8} {'TP':>6} {'FP':>6} {'TN':>6} {'FN':>6} {'Accuracy':>10}")
        print("-" * 80)
        
        for reliability in sorted(reliabilities):
            rel_df = self.df[self.df['Reliability_Score'] == reliability]
            
            tp = len(rel_df[(rel_df['Y_N_MODEL'] == 'YES') & (rel_df['Y_N_TAG'] == 'YES')])
            fp = len(rel_df[(rel_df['Y_N_MODEL'] == 'YES') & (rel_df['Y_N_TAG'] == 'NO')])
            tn = len(rel_df[(rel_df['Y_N_MODEL'] == 'NO') & (rel_df['Y_N_TAG'] == 'NO')])
            fn = len(rel_df[(rel_df['Y_N_MODEL'] == 'NO') & (rel_df['Y_N_TAG'] == 'YES')])
            
            total = len(rel_df)
            accuracy = (tp + tn) / total if total > 0 else 0
            
            print(f"{reliability:<30} {total:>8} {tp:>6} {fp:>6} {tn:>6} {fn:>6} {accuracy:>9.1%}")
        
        print()
    
    def analyze_error_examples(self):
        """
        ניתוח דוגמאות שגיאות
        """
        print("\n🔬 Error Examples Analysis:")
        print("=" * 80)
        
        # False Positives
        fp_count = len(self.errors['false_positives'])
        print(f"\n❌ False Positives ({fp_count}): Model said YES, but actually NO")
        print("-" * 80)
        
        if fp_count > 0:
            print("First 5 examples:")
            for idx, (_, row) in enumerate(self.errors['false_positives'].head(5).iterrows(), 1):
                content = str(row['Content_Body'])[:60] + "..." if len(str(row['Content_Body'])) > 60 else str(row['Content_Body'])
                extracted = row.get('Extracted_Coordinate', 'N/A')
                print(f"\n{idx}. Report {row.get('Report_ID', 'N/A')}:")
                print(f"   Content: {content}")
                print(f"   Extracted: {extracted}")
                print(f"   → Model thought it found coordinate, but tagger says NO")
        else:
            print("✓ No false positives - excellent!")
        
        # False Negatives
        fn_count = len(self.errors['false_negatives'])
        print(f"\n\n⚠️ False Negatives ({fn_count}): Model said NO, but actually YES")
        print("-" * 80)
        
        if fn_count > 0:
            print("First 5 examples:")
            for idx, (_, row) in enumerate(self.errors['false_negatives'].head(5).iterrows(), 1):
                content = str(row['Content_Body'])[:60] + "..." if len(str(row['Content_Body'])) > 60 else str(row['Content_Body'])
                print(f"\n{idx}. Report {row.get('Report_ID', 'N/A')}:")
                print(f"   Content: {content}")
                print(f"   → Model missed this coordinate!")
        else:
            print("✓ No false negatives - excellent!")
        
        print()
    
    def analyze_sector_reliability_cross(self):
        """
        ניתוח צולב: גזרה × אמינות לשגיאות
        זיהוי קשרים בין מגזרים לסוגי מקורות באזורי שגיאה
        """
        print("\n🔍 Cross-Analysis: Sector × Reliability for Errors")
        print("=" * 80)
        
        if 'Sector' not in self.df.columns or 'Reliability_Score' not in self.df.columns:
            print("⚠️ Required columns not found - skipping cross-analysis")
            return
        
        # Get all errors
        errors_df = self.df[
            ((self.df['Y_N_MODEL'] == 'YES') & (self.df['Y_N_TAG'] == 'NO')) |
            ((self.df['Y_N_MODEL'] == 'NO') & (self.df['Y_N_TAG'] == 'YES'))
        ]
        
        if len(errors_df) == 0:
            print("✓ No errors to analyze!")
            return
        
        print(f"\nTotal errors to analyze: {len(errors_df)}")
        
        # Find worst sector
        sector_error_counts = []
        for sector in self.df['Sector'].unique():
            sector_errors = errors_df[errors_df['Sector'] == sector]
            sector_error_counts.append((sector, len(sector_errors)))
        
        sector_error_counts.sort(key=lambda x: x[1], reverse=True)
        worst_sector = sector_error_counts[0][0] if sector_error_counts else None
        
        if worst_sector:
            worst_errors = errors_df[errors_df['Sector'] == worst_sector]
            
            print(f"\n📍 Focus: {worst_sector} ({len(worst_errors)} errors)")
            print("-" * 80)
            
            for rel in sorted(worst_errors['Reliability_Score'].unique()):
                rel_errors = worst_errors[worst_errors['Reliability_Score'] == rel]
                fp = len(rel_errors[rel_errors['Y_N_MODEL'] == 'YES'])
                fn = len(rel_errors[rel_errors['Y_N_MODEL'] == 'NO'])
                total_in_sector = len(self.df[(self.df['Sector'] == worst_sector) & 
                                               (self.df['Reliability_Score'] == rel)])
                print(f"  • {rel}: {len(rel_errors)} שגיאות מתוך {total_in_sector} דוחות ({fp} FP, {fn} FN)")
        
        # All sectors breakdown
        print(f"\n📊 All Sectors - Error Breakdown by Reliability:")
        print("-" * 80)
        
        for sector in sorted(self.df['Sector'].unique()):
            sector_errors = errors_df[errors_df['Sector'] == sector]
            if len(sector_errors) > 0:
                print(f"\n{sector} ({len(sector_errors)} errors):")
                rel_dist = sector_errors['Reliability_Score'].value_counts().sort_index()
                for rel, count in rel_dist.items():
                    print(f"  - {rel}: {count} error(s)")
        
        # Key insight
        print(f"\n💡 Key Insight:")
        print("-" * 80)
        d4_errors = len(errors_df[errors_df['Reliability_Score'].str.contains('D4', na=False)])
        print(f"  • {d4_errors} מתוך {len(errors_df)} שגיאות ({d4_errors/len(errors_df):.1%}) מגיעות מרמת D4")
        print(f"  • רוב השגיאות אינן תלויות במגזר אלא בסוג המקור")
        print()
    
    def generate_observations(self):
        """
        יצירת תצפיות בזהירות - ללא מסקנות חותכות
        """
        print("\n💡 Observations and Analysis:")
        print("=" * 80)
        
        precision = self.metrics['Precision']
        recall = self.metrics['Recall']
        f1 = self.metrics['F1-Score']
        accuracy = self.metrics['Accuracy']
        
        fp = self.confusion_matrix['FP']
        fn = self.confusion_matrix['FN']
        
        print("\n📊 Performance Summary:")
        print(f"   Accuracy:  {accuracy:.1%}")
        print(f"   Precision: {precision:.1%}")
        print(f"   Recall:    {recall:.1%}")
        print(f"   F1-Score:  {f1:.1%}")
        
        print("\n🔍 Observations:")
        
        # Accuracy observation
        if accuracy >= 0.90:
            print(f"\n  • הדיוק הכללי של {accuracy:.1%} עשוי להצביע על ביצועים טובים")
        elif accuracy >= 0.80:
            print(f"\n  • הדיוק הכללי של {accuracy:.1%} עשוי להצביע על ביצועים סבירים")
        else:
            print(f"\n  • הדיוק הכללי של {accuracy:.1%} עשוי לעורר שאלות לגבי הביצועים")
        
        # Error patterns
        if fp > 0:
            print(f"\n  • נצפו {fp} מקרים של False Positive")
            print("    (המודל זיהה נ.צ במקומות בהם לא קיימת)")
            
            # Check if all FP are from D4
            if 'Reliability_Score' in self.df.columns:
                fp_errors = self.df[(self.df['Y_N_MODEL'] == 'YES') & (self.df['Y_N_TAG'] == 'NO')]
                if len(fp_errors) > 0:
                    d4_fp_count = len(fp_errors[fp_errors['Reliability_Score'].str.contains('D4', na=False)])
                    if d4_fp_count == len(fp_errors):
                        print(f"    ⚠️ כל {d4_fp_count} ה-FP (100%) מגיעות מדרגת אמינות D4!")
                        print("    → המלצה מיידית: הוספת validation נוסף לחילוצים מ-D4")
        
        if fn > 0:
            print(f"\n  • נצפו {fn} מקרים של False Negative")
            print("    (המודל החמיץ נ.צ קיימות)")
        
        # Balance observation
        if fp > 0 and fn > 0:
            ratio = fp / fn
            if ratio > 2:
                print(f"\n  • יחס FP:FN של {ratio:.1f}:1 עשוי להצביע על חילוץ יתר")
            elif ratio < 0.5:
                print(f"\n  • יחס FP:FN של {ratio:.1f}:1 עשוי להצביע על חילוץ חסר")
            else:
                print(f"\n  • יחס FP:FN של {ratio:.1f}:1 נראה מאוזן יחסית")
        
        print("\n  • מומלץ להפעיל שיקול דעת מקצועי בהתחשב בהקשר התפעולי")
        print()
    
    def save_report(self, output_dir='outputs/reports'):
        """
        שמירת דוח מפורט ומקיף
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        report_file = output_path / 'performance_evaluation_report.txt'
        
        print(f"\nSaving detailed report to: {report_file}")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write("PERFORMANCE EVALUATION REPORT\n")
            f.write("דוח הערכת ביצועים - מודל חילוץ נ.צ\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tagged File: {self.tagged_file}\n")
            f.write(f"Total Records Evaluated: {len(self.df)}\n")
            f.write("\n")
            
            # === CONFUSION MATRIX ===
            f.write("=" * 80 + "\n")
            f.write("1. CONFUSION MATRIX\n")
            f.write("=" * 80 + "\n")
            tp = self.confusion_matrix['TP']
            fp = self.confusion_matrix['FP']
            tn = self.confusion_matrix['TN']
            fn = self.confusion_matrix['FN']
            
            f.write("\n                     Actual (Human Tag)\n")
            f.write("                     Positive    Negative\n")
            f.write(f"Predicted    Positive    {tp:4d}        {fp:4d}\n")
            f.write(f"(Model)      Negative    {fn:4d}        {tn:4d}\n")
            f.write("\n")
            f.write(f"TP (True Positive):  {tp:4d} - Model correctly identified coordinates\n")
            f.write(f"FP (False Positive): {fp:4d} - Model incorrectly extracted non-coordinates\n")
            f.write(f"TN (True Negative):  {tn:4d} - Model correctly identified no coordinates\n")
            f.write(f"FN (False Negative): {fn:4d} - Model missed actual coordinates\n")
            f.write("\n")
            
            # === PERFORMANCE METRICS ===
            f.write("=" * 80 + "\n")
            f.write("2. PERFORMANCE METRICS\n")
            f.write("=" * 80 + "\n\n")
            
            for metric_name, metric_value in self.metrics.items():
                f.write(f"{metric_name:<15}: {metric_value:7.2%}\n")
            
            f.write("\nInterpretation:\n")
            accuracy = self.metrics['Accuracy']
            if accuracy >= 0.95:
                f.write("  EXCELLENT - Model accuracy is very high (>=95%)\n")
            elif accuracy >= 0.85:
                f.write("  GOOD - Model accuracy is satisfactory (>=85%)\n")
            elif accuracy >= 0.75:
                f.write("  FAIR - Model accuracy is acceptable (>=75%)\n")
            else:
                f.write("  POOR - Model accuracy is below acceptable threshold (<75%)\n")
            f.write("\n")
            
            # === ERROR ANALYSIS BY SECTOR ===
            f.write("=" * 80 + "\n")
            f.write("3. ERROR ANALYSIS BY SECTOR\n")
            f.write("=" * 80 + "\n\n")
            
            if 'Sector' in self.df.columns:
                sectors = sorted(self.df['Sector'].unique())
                f.write(f"{'Sector':<25} {'Total':>8} {'TP':>6} {'FP':>6} {'TN':>6} {'FN':>6} {'Accuracy':>10}\n")
                f.write("-" * 80 + "\n")
                
                sector_errors = []
                for sector in sectors:
                    sector_df = self.df[self.df['Sector'] == sector]
                    
                    tp_s = len(sector_df[(sector_df['Y_N_MODEL'] == 'YES') & (sector_df['Y_N_TAG'] == 'YES')])
                    fp_s = len(sector_df[(sector_df['Y_N_MODEL'] == 'YES') & (sector_df['Y_N_TAG'] == 'NO')])
                    tn_s = len(sector_df[(sector_df['Y_N_MODEL'] == 'NO') & (sector_df['Y_N_TAG'] == 'NO')])
                    fn_s = len(sector_df[(sector_df['Y_N_MODEL'] == 'NO') & (sector_df['Y_N_TAG'] == 'YES')])
                    
                    total_s = len(sector_df)
                    acc_s = (tp_s + tn_s) / total_s if total_s > 0 else 0
                    errors_s = fp_s + fn_s
                    
                    f.write(f"{sector:<25} {total_s:>8} {tp_s:>6} {fp_s:>6} {tn_s:>6} {fn_s:>6} {acc_s:>9.1%}\n")
                    sector_errors.append((sector, errors_s, fp_s, fn_s))
                
                sector_errors.sort(key=lambda x: x[1], reverse=True)
                
                f.write("\nKey Findings:\n")
                if sector_errors[0][1] > 0:
                    f.write(f"  - Most errors in: {sector_errors[0][0]} ({sector_errors[0][1]} total: {sector_errors[0][2]} FP, {sector_errors[0][3]} FN)\n")
                best_sector = min(sector_errors, key=lambda x: x[1])
                f.write(f"  - Best performance: {best_sector[0]} ({best_sector[1]} errors)\n")
                f.write("\n")
            else:
                f.write("Sector column not found - skipping sector analysis\n\n")
            
            # === ERROR ANALYSIS BY RELIABILITY ===
            f.write("=" * 80 + "\n")
            f.write("4. ERROR ANALYSIS BY RELIABILITY SCORE (SOURCE TYPE)\n")
            f.write("=" * 80 + "\n\n")
            
            if 'Reliability_Score' in self.df.columns:
                reliabilities = sorted(self.df['Reliability_Score'].unique())
                f.write(f"{'Reliability':<30} {'Total':>8} {'TP':>6} {'FP':>6} {'TN':>6} {'FN':>6} {'Accuracy':>10}\n")
                f.write("-" * 80 + "\n")
                
                reliability_stats = []
                for reliability in reliabilities:
                    rel_df = self.df[self.df['Reliability_Score'] == reliability]
                    
                    tp_r = len(rel_df[(rel_df['Y_N_MODEL'] == 'YES') & (rel_df['Y_N_TAG'] == 'YES')])
                    fp_r = len(rel_df[(rel_df['Y_N_MODEL'] == 'YES') & (rel_df['Y_N_TAG'] == 'NO')])
                    tn_r = len(rel_df[(rel_df['Y_N_MODEL'] == 'NO') & (rel_df['Y_N_TAG'] == 'NO')])
                    fn_r = len(rel_df[(rel_df['Y_N_MODEL'] == 'NO') & (rel_df['Y_N_TAG'] == 'YES')])
                    
                    total_r = len(rel_df)
                    acc_r = (tp_r + tn_r) / total_r if total_r > 0 else 0
                    errors_r = fp_r + fn_r
                    
                    f.write(f"{reliability:<30} {total_r:>8} {tp_r:>6} {fp_r:>6} {tn_r:>6} {fn_r:>6} {acc_r:>9.1%}\n")
                    reliability_stats.append((reliability, errors_r, acc_r, total_r))
                
                # Dynamic analysis
                reliability_stats.sort(key=lambda x: x[1])  # Sort by errors
                best_rel = reliability_stats[0] if reliability_stats else None
                worst_rel = reliability_stats[-1] if reliability_stats else None
                
                f.write("\nObservations:\n")
                if best_rel and worst_rel:
                    f.write(f"  - רמת אמינות '{best_rel[0]}' נצפתה עם {best_rel[1]} שגיאות ({best_rel[2]:.1%} דיוק) מתוך {best_rel[3]} דוחות\n")
                    f.write(f"  - רמת אמינות '{worst_rel[0]}' נצפתה עם {worst_rel[1]} שגיאות ({worst_rel[2]:.1%} דיוק) מתוך {worst_rel[3]} דוחות\n")
                    f.write("  - התפלגות הדגימה עשויה להשפיע על הממצאים\n")
                    f.write("  - מומלץ להפעיל שיקול דעת בהתחשב בהקשר התפעולי\n")
                f.write("\n")
            else:
                f.write("Reliability_Score column not found - skipping reliability analysis\n\n")
            
            # === ERROR EXAMPLES ===
            f.write("=" * 80 + "\n")
            f.write("5. ERROR EXAMPLES\n")
            f.write("=" * 80 + "\n\n")
            
            # False Positives
            fp_count = len(self.errors['false_positives'])
            f.write(f"FALSE POSITIVES ({fp_count}): Model said YES, but actually NO\n")
            f.write("-" * 80 + "\n\n")
            
            if fp_count > 0:
                for idx, (_, row) in enumerate(self.errors['false_positives'].head(5).iterrows(), 1):
                    content = str(row['Content_Body'])
                    extracted = row.get('Extracted_Coordinate', 'N/A')
                    f.write(f"Example {idx}:\n")
                    f.write(f"  Report ID: {row.get('Report_ID', 'N/A')}\n")
                    f.write(f"  Content: {content}\n")
                    f.write(f"  Model extracted: {extracted}\n")
                    f.write(f"  Issue: Not a valid coordinate\n\n")
            else:
                f.write("No false positives - excellent!\n\n")
            
            # False Negatives
            fn_count = len(self.errors['false_negatives'])
            f.write(f"FALSE NEGATIVES ({fn_count}): Model said NO, but actually YES\n")
            f.write("-" * 80 + "\n\n")
            
            if fn_count > 0:
                for idx, (_, row) in enumerate(self.errors['false_negatives'].head(5).iterrows(), 1):
                    content = str(row['Content_Body'])
                    f.write(f"Example {idx}:\n")
                    f.write(f"  Report ID: {row.get('Report_ID', 'N/A')}\n")
                    f.write(f"  Content: {content}\n")
                    f.write(f"  Issue: Model missed this coordinate\n\n")
            else:
                f.write("No false negatives - excellent!\n\n")
            
            # === CROSS-ANALYSIS: SECTOR × RELIABILITY ===
            f.write("=" * 80 + "\n")
            f.write("6. CROSS-ANALYSIS: SECTOR × RELIABILITY\n")
            f.write("=" * 80 + "\n\n")
            
            if 'Sector' in self.df.columns and 'Reliability_Score' in self.df.columns:
                # Get all errors
                errors_df = self.df[
                    ((self.df['Y_N_MODEL'] == 'YES') & (self.df['Y_N_TAG'] == 'NO')) |
                    ((self.df['Y_N_MODEL'] == 'NO') & (self.df['Y_N_TAG'] == 'YES'))
                ]
                
                if len(errors_df) > 0:
                    # Find worst sector
                    sector_error_counts = []
                    for sector in self.df['Sector'].unique():
                        sector_errors = errors_df[errors_df['Sector'] == sector]
                        sector_error_counts.append((sector, len(sector_errors)))
                    
                    sector_error_counts.sort(key=lambda x: x[1], reverse=True)
                    worst_sector = sector_error_counts[0][0] if sector_error_counts else None
                    
                    if worst_sector:
                        worst_errors = errors_df[errors_df['Sector'] == worst_sector]
                        
                        f.write(f"Focus: {worst_sector} ({len(worst_errors)} errors)\n")
                        f.write("-" * 80 + "\n\n")
                        
                        for rel in sorted(worst_errors['Reliability_Score'].unique()):
                            rel_errors = worst_errors[worst_errors['Reliability_Score'] == rel]
                            fp = len(rel_errors[rel_errors['Y_N_MODEL'] == 'YES'])
                            fn = len(rel_errors[rel_errors['Y_N_MODEL'] == 'NO'])
                            total_in_sector = len(self.df[(self.df['Sector'] == worst_sector) & 
                                                           (self.df['Reliability_Score'] == rel)])
                            f.write(f"  • {rel}: {len(rel_errors)} שגיאות מתוך {total_in_sector} דוחות ({fp} FP, {fn} FN)\n")
                    
                    # All sectors breakdown
                    f.write(f"\n\nAll Sectors - Error Breakdown by Reliability:\n")
                    f.write("-" * 80 + "\n\n")
                    
                    for sector in sorted(self.df['Sector'].unique()):
                        sector_errors = errors_df[errors_df['Sector'] == sector]
                        if len(sector_errors) > 0:
                            f.write(f"{sector} ({len(sector_errors)} errors):\n")
                            rel_dist = sector_errors['Reliability_Score'].value_counts().sort_index()
                            for rel, count in rel_dist.items():
                                f.write(f"  - {rel}: {count} error(s)\n")
                            f.write("\n")
                    
                    # Key insight
                    f.write(f"Key Insight:\n")
                    f.write("-" * 40 + "\n")
                    d4_errors = len(errors_df[errors_df['Reliability_Score'].str.contains('D4', na=False)])
                    f.write(f"  • {d4_errors} מתוך {len(errors_df)} שגיאות ({d4_errors/len(errors_df):.1%}) מגיעות מרמת D4\n")
                    f.write(f"  • רוב השגיאות אינן תלויות במגזר אלא בסוג המקור\n")
                    f.write(f"  • המודל מתקשה עם דיווחים בדרגת אמינות נמוכה יותר\n")
                    f.write("\n")
                    
                    # Examples of D4 errors
                    f.write(f"דוגמאות False Positive מ-D4 (מספר 6 ספרות שנראה כמו נ.צ אך לא):\n")
                    f.write("-" * 40 + "\n")
                    d4_fp = errors_df[(errors_df['Reliability_Score'].str.contains('D4', na=False)) & 
                                      (errors_df['Y_N_MODEL'] == 'YES') & 
                                      (errors_df['Y_N_TAG'] == 'NO')]
                    
                    for idx, (_, row) in enumerate(d4_fp.head(3).iterrows(), 1):
                        content = str(row['Content_Body'])[:60] if 'Content_Body' in row else 'N/A'
                        extracted = row.get('Extracted_Coordinate', 'N/A')
                        if pd.notna(extracted) and extracted != '':
                            extracted = int(float(extracted))
                        else:
                            extracted = 'N/A'
                        f.write(f"  ID {row['Report_ID']}: \"{content}\" → חילוץ: {extracted}\n")
                    f.write("\n")
                else:
                    f.write("No errors to analyze in cross-analysis.\n\n")
            else:
                f.write("Required columns not found for cross-analysis.\n\n")
            
            # === OBSERVATIONS ===
            f.write("=" * 80 + "\n")
            f.write("7. OBSERVATIONS AND ANALYSIS\n")
            f.write("=" * 80 + "\n\n")
            
            precision = self.metrics['Precision']
            recall = self.metrics['Recall']
            f1 = self.metrics['F1-Score']
            accuracy = self.metrics['Accuracy']
            
            f.write("Performance Summary:\n")
            f.write("-" * 40 + "\n")
            f.write(f"  Accuracy:  {accuracy:.1%}\n")
            f.write(f"  Precision: {precision:.1%}\n")
            f.write(f"  Recall:    {recall:.1%}\n")
            f.write(f"  F1-Score:  {f1:.1%}\n\n")
            
            f.write("Observations:\n")
            f.write("-" * 40 + "\n")
            
            # Accuracy observation
            if accuracy >= 0.90:
                f.write(f"  • הדיוק הכללי של {accuracy:.1%} עשוי להצביע על ביצועים טובים\n")
            elif accuracy >= 0.80:
                f.write(f"  • הדיוק הכללי של {accuracy:.1%} עשוי להצביע על ביצועים סבירים\n")
            else:
                f.write(f"  • הדיוק הכללי של {accuracy:.1%} עשוי לעורר שאלות לגבי הביצועים\n")
            
            # Error patterns
            if fp > 0:
                f.write(f"\n  • נצפו {fp} מקרים של False Positive\n")
                f.write("    (המודל זיהה נ.צ במקומות בהם לא קיימת)\n")
                
                # Check if all FP are from D4
                if 'Reliability_Score' in self.df.columns:
                    fp_errors = self.df[(self.df['Y_N_MODEL'] == 'YES') & (self.df['Y_N_TAG'] == 'NO')]
                    if len(fp_errors) > 0:
                        d4_fp_count = len(fp_errors[fp_errors['Reliability_Score'].str.contains('D4', na=False)])
                        if d4_fp_count == len(fp_errors):
                            f.write(f"    ⚠️ כל {d4_fp_count} ה-FP (100%) מגיעות מדרגת אמינות D4!\n")
                            f.write("    → המלצה מיידית: הוספת validation נוסף לחילוצים מ-D4\n")
                        else:
                            f.write("    → כדאי לשקול בדיקת דפוסי המילות העוגן\n")
                else:
                    f.write("    → כדאי לשקול בדיקת דפוסי המילות העוגן\n")
            
            if fn > 0:
                f.write(f"\n  • נצפו {fn} מקרים של False Negative\n")
                f.write("    (המודל החמיץ נ.צ קיימות)\n")
                f.write("    → כדאי לשקול הרחבת דפוסי החילוץ\n")
            
            # Balance observation
            if fp > 0 and fn > 0:
                ratio = fp / fn
                if ratio > 2:
                    f.write(f"\n  • יחס FP:FN של {ratio:.1f}:1 עשוי להצביע על חילוץ יתר\n")
                elif ratio < 0.5:
                    f.write(f"\n  • יחס FP:FN של {ratio:.1f}:1 עשוי להצביע על חילוץ חסר\n")
                else:
                    f.write(f"\n  • יחס FP:FN של {ratio:.1f}:1 נראה מאוזן יחסית\n")
            
            f.write("\n  • מומלץ להפעיל שיקול דעת מקצועי בהתחשב בהקשר התפעולי\n")
            f.write("  • ממצאים אלו מבוססים על המדגם הנוכחי ועשויים להשתנות\n")
            f.write("\n")
            
            # === END ===
            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        print(f"OK Report saved successfully")
        print()
    
    def run_evaluation(self):
        """
        הרצת תהליך ההערכה המלא
        """
        try:
            # Load data
            self.load_tagged_data()
            
            # Calculate confusion matrix
            self.calculate_confusion_matrix()
            
            # Calculate metrics
            self.calculate_metrics()
            
            # Error analysis
            self.analyze_errors_by_sector()
            self.analyze_errors_by_reliability()
            self.analyze_error_examples()
            
            # Cross-analysis: Sector × Reliability
            self.analyze_sector_reliability_cross()
            
            # Generate observations
            self.generate_observations()
            
            # Save report
            self.save_report()
            
            print("=" * 80)
            print("✅ EVALUATION COMPLETE!")
            print("=" * 80)
            print()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error during evaluation: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """
    נקודת כניסה ראשית
    """
    # Try different possible file locations
    possible_files = [
        'data/tagging/tagging_task_tagged.csv',
        'data/tagging/דאטה מתויג לתהילה.csv',
        'data/tagging/tagging_task.csv'
    ]
    
    tagged_file = None
    for file_path in possible_files:
        if Path(file_path).exists():
            tagged_file = file_path
            break
    
    if not tagged_file:
        print("❌ Error: Could not find tagged file!")
        print("\nSearched for:")
        for f in possible_files:
            print(f"  - {f}")
        print("\nPlease ensure the tagged file is in data/tagging/ directory")
        return
    
    print(f"Found tagged file: {tagged_file}\n")
    
    # Create evaluator and run
    evaluator = PerformanceEvaluator(tagged_file)
    success = evaluator.run_evaluation()
    
    if success:
        print("📊 Check the detailed report at: outputs/reports/performance_evaluation_report.txt")
    else:
        print("⚠️ Evaluation completed with errors")


if __name__ == '__main__':
    main()

