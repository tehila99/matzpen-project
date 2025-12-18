"""
Tagging Sample Generator - QA Pipeline
=======================================
שלב ד': יצירת מדגם תיוג מרובד (Stratified Sample)

This module creates a balanced, stratified sample of 100 reports for manual tagging:
- 40 reports with coordinates (positive cases)
- 40 reports without coordinates (negative cases)
- 20 edge cases (challenging examples)
"""

import pandas as pd
import numpy as np
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


class TaggingSampleGenerator:
    """
    מחולל מדגם תיוג חכם - בוחר דיווחים מגוונים ומאתגרים
    """
    
    def __init__(self, df):
        self.df = df.copy()
        self.sample = pd.DataFrame()
        self.stats = {
            'positive_samples': [],
            'negative_samples': [],
            'edge_cases': []
        }
    
    def calculate_edge_case_scores(self):
        """
        חישוב ציון "מקרה קצה" לכל דיווח
        ככל שהציון גבוה יותר, הדיווח יותר מאתגר/מעניין לתיוג
        """
        print("Calculating edge case scores...")
        
        self.df['edge_score'] = 0
        self.df['edge_reasons'] = ''
        
        # חישוב אורך תוכן
        self.df['content_length'] = self.df['Content_Body'].str.len()
        
        # ספירת מספרים בטקסט (כל רצף של ספרות)
        self.df['num_count'] = self.df['Content_Body'].apply(
            lambda x: len(re.findall(r'\d+', str(x))) if pd.notna(x) else 0
        )
        
        # ספירת מספרים בני 6 ספרות
        self.df['six_digit_count'] = self.df['Content_Body'].apply(
            lambda x: len(re.findall(r'\d{6}', str(x))) if pd.notna(x) else 0
        )
        
        # ספירת מספרים בני 5-7 ספרות (קרובים ל-6)
        self.df['near_six_digit_count'] = self.df['Content_Body'].apply(
            lambda x: len(re.findall(r'\d{5}|\d{7}', str(x))) if pd.notna(x) else 0
        )
        
        reasons_list = []
        
        for idx, row in self.df.iterrows():
            score = 0
            reasons = []
            
            # 1. טקסט קצר מאוד (< 30 תווים)
            if row['content_length'] < 30:
                score += 3
                reasons.append('very_short_text')
            
            # 2. טקסט ארוך מאוד (> 200 תווים)
            if row['content_length'] > 200:
                score += 2
                reasons.append('very_long_text')
            
            # 3. מספרים רבים בטקסט
            if row['num_count'] >= 5:
                score += 3
                reasons.append('many_numbers')
            
            # 4. מספרים בני 5 או 7 ספרות (קרובים ל-6)
            if row['near_six_digit_count'] > 0:
                score += 4
                reasons.append('near_6_digit')
            
            # 5. מספר מספרים בני 6 ספרות (פוטנציאל לבלבול)
            if row['six_digit_count'] > 1:
                score += 5
                reasons.append('multiple_6_digits')
            
            # 6. יש 6 ספרות אבל לא זוהה (False Negative potential)
            if row['Has_Coordinate'] == 0 and row['six_digit_count'] > 0:
                score += 6
                reasons.append('missed_potential_coord')
            
            # 7. זוהה נ.צ אבל יש מספרים נוספים (False Positive potential)
            if row['Has_Coordinate'] == 1 and row['six_digit_count'] > 1:
                score += 4
                reasons.append('multiple_candidates')
            
            # 8. אמינות נמוכה (D4 או F)
            if pd.notna(row['Reliability_Score']):
                if 'D' in str(row['Reliability_Score']) or 'F' in str(row['Reliability_Score']):
                    score += 2
                    reasons.append('low_reliability')
            
            # 9. מילות עוגן חלקיות או לא תקניות
            content = str(row['Content_Body']).lower()
            if 'נצ' in content and 'נ.צ' not in content:
                score += 3
                reasons.append('non_standard_anchor')
            
            # 10. נ.צ בתחילת או סוף הטקסט (10 תווים ראשונים/אחרונים)
            if row['Has_Coordinate'] == 1:
                coord = str(row['Extracted_Coordinate'])
                coord_pos = content.find(coord)
                if coord_pos >= 0:
                    if coord_pos < 15 or coord_pos > row['content_length'] - 20:
                        score += 2
                        reasons.append('coord_at_edge')
            
            self.df.at[idx, 'edge_score'] = score
            reasons_list.append(', '.join(reasons) if reasons else '')
        
        self.df['edge_reasons'] = reasons_list
        print(f"[OK] Edge case scores calculated (range: {self.df['edge_score'].min()}-{self.df['edge_score'].max()})")
    
    def select_positive_samples(self, n=40, exclude_report_ids=None):
        """
        בחירת 40 דיווחים חיוביים (עם נ.צ) - גיוון מקסימלי
        
        Args:
            n: מספר דגימות לבחור
            exclude_report_ids: Report_IDs לא לבחור (למניעת כפילויות)
        """
        print(f"\nSelecting {n} positive samples (with coordinates)...")
        
        positive_df = self.df[self.df['Has_Coordinate'] == 1].copy()
        
        # סינון Report_IDs שכבר נבחרו
        if exclude_report_ids is not None and len(exclude_report_ids) > 0:
            positive_df = positive_df[~positive_df['Report_ID'].isin(exclude_report_ids)]
            print(f"  (Excluding {len(exclude_report_ids)} already selected IDs)")
        
        if len(positive_df) < n:
            print(f"[WARNING] Only {len(positive_df)} positive samples available")
            return positive_df
        
        # אסטרטגיית דגימה מרובדת
        selected_report_ids = set()
        samples = []
        
        # 1. דגימה לפי גזרה (8 מכל גזרה)
        sectors = positive_df['Sector'].unique()
        per_sector = n // len(sectors)
        
        for sector in sectors:
            sector_df = positive_df[
                (positive_df['Sector'] == sector) & 
                (~positive_df['Report_ID'].isin(selected_report_ids))
            ]
            if len(sector_df) > 0:
                # בחירה רנדומלית אבל מגוונת
                sample_size = min(per_sector, len(sector_df))
                # מיון לפי edge_score כדי לקחת מקרים מעניינים
                sector_sample = sector_df.nlargest(sample_size * 2, 'edge_score').sample(
                    n=sample_size, random_state=42
                )
                samples.append(sector_sample)
                selected_report_ids.update(sector_sample['Report_ID'].tolist())
        
        result_df = pd.concat(samples) if samples else pd.DataFrame()
        
        # 2. אם חסרים - השלם מהכלל
        if len(result_df) < n:
            remaining = n - len(result_df)
            remaining_df = positive_df[~positive_df['Report_ID'].isin(selected_report_ids)]
            if len(remaining_df) > 0:
                additional = remaining_df.sample(n=min(remaining, len(remaining_df)), random_state=42)
                result_df = pd.concat([result_df, additional])
        
        # 3. אם יש יותר מדי - קח את המגוונים ביותר
        if len(result_df) > n:
            result_df = result_df.sample(n=n, random_state=42)
        
        print(f"[OK] Selected {len(result_df)} positive samples")
        print(f"  - Sectors covered: {result_df['Sector'].nunique()}")
        print(f"  - Patterns used: {result_df['Extraction_Pattern'].nunique()}")
        print(f"  - Urgency levels: {result_df['Report_Urgency'].nunique()}")
        
        return result_df
    
    def select_negative_samples(self, n=40, exclude_report_ids=None):
        """
        בחירת 40 דיווחים שליליים (בלי נ.צ) - גיוון מקסימלי
        
        Args:
            n: מספר דגימות לבחור
            exclude_report_ids: Report_IDs לא לבחור (למניעת כפילויות)
        """
        print(f"\nSelecting {n} negative samples (without coordinates)...")
        
        negative_df = self.df[self.df['Has_Coordinate'] == 0].copy()
        
        # סינון Report_IDs שכבר נבחרו
        if exclude_report_ids is not None and len(exclude_report_ids) > 0:
            negative_df = negative_df[~negative_df['Report_ID'].isin(exclude_report_ids)]
            print(f"  (Excluding {len(exclude_report_ids)} already selected IDs)")
        
        if len(negative_df) < n:
            print(f"[WARNING] Only {len(negative_df)} negative samples available")
            return negative_df
        
        selected_report_ids = set()
        samples = []
        
        # חלוקה לקטגוריות:
        # 1. ללא מספרים בכלל (15 מקרים)
        no_numbers = negative_df[
            (negative_df['num_count'] == 0) & 
            (~negative_df['Report_ID'].isin(selected_report_ids))
        ]
        if len(no_numbers) > 0:
            sample = no_numbers.sample(n=min(15, len(no_numbers)), random_state=42)
            samples.append(sample)
            selected_report_ids.update(sample['Report_ID'].tolist())
        
        # 2. עם מספרים אבל לא 6 ספרות (15 מקרים)
        with_numbers_not_6 = negative_df[
            (negative_df['num_count'] > 0) & 
            (negative_df['six_digit_count'] == 0) &
            (~negative_df['Report_ID'].isin(selected_report_ids))
        ]
        if len(with_numbers_not_6) > 0:
            sample = with_numbers_not_6.sample(n=min(15, len(with_numbers_not_6)), random_state=42)
            samples.append(sample)
            selected_report_ids.update(sample['Report_ID'].tolist())
        
        # 3. עם 6 ספרות אבל לא זוהה (פוטנציאל ל-False Negative) (10 מקרים)
        potential_fn = negative_df[
            (negative_df['six_digit_count'] > 0) &
            (~negative_df['Report_ID'].isin(selected_report_ids))
        ]
        if len(potential_fn) > 0:
            sample = potential_fn.nlargest(min(10, len(potential_fn)), 'edge_score')
            samples.append(sample)
            selected_report_ids.update(sample['Report_ID'].tolist())
        
        result_df = pd.concat(samples) if samples else pd.DataFrame()
        
        # השלמה אם חסר
        if len(result_df) < n:
            remaining = n - len(result_df)
            remaining_df = negative_df[~negative_df['Report_ID'].isin(selected_report_ids)]
            if len(remaining_df) > 0:
                additional = remaining_df.sample(n=min(remaining, len(remaining_df)), random_state=42)
                result_df = pd.concat([result_df, additional])
        
        # צמצום אם יש יותר מדי
        if len(result_df) > n:
            result_df = result_df.drop_duplicates(subset=['Report_ID']).sample(n=n, random_state=42)
        
        print(f"[OK] Selected {len(result_df)} negative samples")
        print(f"  - With no numbers: {len(result_df[result_df['num_count'] == 0])}")
        print(f"  - With 6-digit numbers: {len(result_df[result_df['six_digit_count'] > 0])}")
        print(f"  - Sectors covered: {result_df['Sector'].nunique()}")
        
        return result_df
    
    def select_edge_cases(self, n=20, exclude_report_ids=None):
        """
        בחירת 20 מקרי קצה - המקרים המאתגרים ביותר
        כפיית איזון: בדיוק מחצית חיוביים ומחצית שליליים
        
        Args:
            n: מספר מקרי קצה לבחור
            exclude_report_ids: Report_IDs שכבר נבחרו (למניעת כפילויות)
        """
        print(f"\nSelecting {n} edge cases (most challenging)...")
        print(f"  Strategy: Force balance - {n//2} positive + {n//2} negative")
        
        # סינון דיווחים שכבר נבחרו
        available_df = self.df.copy()
        if exclude_report_ids is not None and len(exclude_report_ids) > 0:
            available_df = available_df[~available_df['Report_ID'].isin(exclude_report_ids)]
            print(f"  (Excluding {len(exclude_report_ids)} already selected reports)")
        
        # חלוקה לחיוביים ושליליים
        available_positive = available_df[available_df['Has_Coordinate'] == 1]
        available_negative = available_df[available_df['Has_Coordinate'] == 0]
        
        # כפיית בחירה של בדיוק n//2 מכל סוג
        n_per_type = n // 2
        
        # בחירת חיוביים - הכי מאתגרים
        if len(available_positive) >= n_per_type:
            positive_edges = available_positive.nlargest(n_per_type, 'edge_score')
            print(f"  ✓ Selected {len(positive_edges)} positive edge cases (score: {positive_edges['edge_score'].mean():.2f} avg)")
        else:
            positive_edges = available_positive
            print(f"  ! Only {len(positive_edges)} positive available (needed {n_per_type})")
        
        # בחירת שליליים - הכי מאתגרים
        if len(available_negative) >= n_per_type:
            negative_edges = available_negative.nlargest(n_per_type, 'edge_score')
            print(f"  ✓ Selected {len(negative_edges)} negative edge cases (score: {negative_edges['edge_score'].mean():.2f} avg)")
        else:
            negative_edges = available_negative
            print(f"  ! Only {len(negative_edges)} negative available (needed {n_per_type})")
        
        # איחוד
        result_df = pd.concat([positive_edges, negative_edges])
        
        # אם חסרים - השלם מכל מה שיש
        if len(result_df) < n:
            remaining = n - len(result_df)
            print(f"  ! Missing {remaining} samples - filling from available pool")
            already_selected_ids = set(result_df['Report_ID'].tolist())
            remaining_df = available_df[~available_df['Report_ID'].isin(already_selected_ids)]
            additional = remaining_df.nlargest(remaining, 'edge_score')
            result_df = pd.concat([result_df, additional])
        
        print(f"[OK] Selected {len(result_df)} edge cases")
        print(f"  - With coordinates: {len(result_df[result_df['Has_Coordinate'] == 1])}")
        print(f"  - Without coordinates: {len(result_df[result_df['Has_Coordinate'] == 0])}")
        print(f"  - Average edge score: {result_df['edge_score'].mean():.2f}")
        
        # הצגת טווח הציונים
        pos_scores = result_df[result_df['Has_Coordinate'] == 1]['edge_score']
        neg_scores = result_df[result_df['Has_Coordinate'] == 0]['edge_score']
        if len(pos_scores) > 0:
            print(f"  - Positive scores: {pos_scores.min():.0f}-{pos_scores.max():.0f}")
        if len(neg_scores) > 0:
            print(f"  - Negative scores: {neg_scores.min():.0f}-{neg_scores.max():.0f}")
        
        return result_df
    
    def generate_sample(self):
        """
        יצירת המדגם המלא - 40+40+20 = 100 דיווחים (ללא כפילויות)
        """
        print("=" * 80)
        print("GENERATING TAGGING SAMPLE")
        print("יצירת מדגם תיוג מרובד")
        print("=" * 80)
        
        # 1. חישוב ציוני Edge Case
        self.calculate_edge_case_scores()
        
        # 2. בחירת דגימות בסדר נכון (למניעת כפילויות)
        positive_sample = self.select_positive_samples(n=40, exclude_report_ids=set())
        
        # שמירת ה-Report_IDs שכבר נבחרו
        selected_report_ids = set(positive_sample['Report_ID'].tolist())
        
        negative_sample = self.select_negative_samples(n=40, exclude_report_ids=selected_report_ids)
        
        # עדכון ה-Report_IDs שנבחרו
        selected_report_ids.update(negative_sample['Report_ID'].tolist())
        
        # בחירת Edge Cases (ללא דיווחים שכבר נבחרו)
        edge_sample = self.select_edge_cases(n=20, exclude_report_ids=selected_report_ids)
        
        # שמירת ה-Report_IDs של ה-edge cases למעקב
        self.edge_case_ids = set(edge_sample['Report_ID'].tolist())
        
        # 3. איחוד הדגימות
        print("\nCombining all samples...")
        self.sample = pd.concat([
            positive_sample,
            negative_sample,
            edge_sample
        ], ignore_index=True)
        
        # בדיקת כפילויות (לא אמורות להיות!)
        initial_size = len(self.sample)
        self.sample = self.sample.drop_duplicates(subset=['Report_ID'], keep='first')
        
        if len(self.sample) < initial_size:
            duplicates_removed = initial_size - len(self.sample)
            print(f"[WARNING] Removed {duplicates_removed} duplicates")
            
            # השלמת החסר
            print(f"[INFO] Filling {duplicates_removed} missing samples...")
            already_selected_ids = set(self.sample['Report_ID'].tolist())
            remaining_df = self.df[~self.df['Report_ID'].isin(already_selected_ids)]
            
            # בחירה לפי edge_score הגבוה ביותר
            additional = remaining_df.nlargest(duplicates_removed, 'edge_score')
            self.sample = pd.concat([self.sample, additional], ignore_index=True)
            print(f"[OK] Added {len(additional)} additional reports")
        
        # 4. ערבוב הדגימות
        self.sample = self.sample.sample(frac=1, random_state=42).reset_index(drop=True)
        
        print(f"\n[OK] Final sample size: {len(self.sample)} reports")
        
        if len(self.sample) == 100:
            print("[SUCCESS] Exactly 100 reports as requested!")
        elif len(self.sample) < 100:
            print(f"[WARNING] Only {len(self.sample)} reports (expected 100)")
        
        return self.sample
    
    def create_tagging_file(self, output_path):
        """
        יצירת קובץ תיוג לשליחה למתייג
        """
        print("\nCreating tagging file...")
        
        # בחירת עמודות רלוונטיות
        tagging_df = self.sample[[
            'Report_ID',
            'Content_Body',
            'Extracted_Coordinate',
            'Has_Coordinate',
            'edge_score',
            'edge_reasons',
            'Sector',
            'Report_Urgency',
            'Reliability_Score'
        ]].copy()
        
        # המרת Extracted_Coordinate ל-STRING (למניעת אובדן 0 מוביל!)
        tagging_df['Extracted_Coordinate'] = tagging_df['Extracted_Coordinate'].apply(
            lambda x: str(int(x)) if pd.notna(x) else ''
        )
        
        # יצירת עמודת Y_N_MODEL
        tagging_df['Y_N_MODEL'] = tagging_df['Has_Coordinate'].apply(
            lambda x: 'Yes' if x == 1 else 'No'
        )
        
        # יצירת עמודת Is_Edge_Case (האם זה מקרה קצה?)
        # רק ה-20 שנבחרו במיוחד בשלב 3 מסומנים כ-edge cases
        tagging_df['Is_Edge_Case'] = tagging_df['Report_ID'].apply(
            lambda x: 'Yes' if x in self.edge_case_ids else 'No'
        )
        
        # יצירת עמודות ריקות למילוי ידני
        tagging_df['Y_N_TAG'] = ''
        tagging_df['Tagged_Coordinate'] = ''
        
        # סידור העמודות
        tagging_df = tagging_df[[
            'Report_ID',
            'Content_Body',
            'Extracted_Coordinate',
            'Y_N_MODEL',
            'Y_N_TAG',
            'Tagged_Coordinate',
            'Is_Edge_Case',
            'Sector',
            'Report_Urgency',
            'Reliability_Score'
        ]]
        
        # שמירה עם dtype מפורש כדי לשמור strings
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # המרה סופית לפני שמירה - וידוא ש-Extracted_Coordinate הוא string
        tagging_df['Extracted_Coordinate'] = tagging_df['Extracted_Coordinate'].astype(str).replace('nan', '')
        
        tagging_df.to_csv(output_path, index=False, encoding='utf-8-sig')  # UTF-8 with BOM for Excel
        
        print(f"[OK] Tagging file saved to: {output_path}")
        
        return tagging_df
    
    def generate_tagging_report(self, output_path):
        """
        יצירת דוח מפורט על המדגם שנוצר
        """
        print("\nGenerating tagging report...")
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("TAGGING SAMPLE GENERATION REPORT")
        report_lines.append("דוח יצירת מדגם תיוג")
        report_lines.append("=" * 80)
        report_lines.append(f"\nGeneration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total Sample Size: {len(self.sample)} reports")
        report_lines.append("\n")
        
        # סטטיסטיקות כלליות
        report_lines.append("-" * 80)
        report_lines.append("SAMPLE COMPOSITION")
        report_lines.append("-" * 80)
        report_lines.append(f"Reports WITH coordinates: {len(self.sample[self.sample['Has_Coordinate'] == 1])}")
        report_lines.append(f"Reports WITHOUT coordinates: {len(self.sample[self.sample['Has_Coordinate'] == 0])}")
        report_lines.append("\n")
        
        # פילוח לפי גזרה
        report_lines.append("-" * 80)
        report_lines.append("BREAKDOWN BY SECTOR")
        report_lines.append("-" * 80)
        sector_breakdown = self.sample.groupby('Sector').agg({
            'Has_Coordinate': ['sum', 'count']
        })
        sector_breakdown.columns = ['With_Coords', 'Total']
        
        for sector, row in sector_breakdown.iterrows():
            report_lines.append(f"{sector}: {int(row['Total'])} reports ({int(row['With_Coords'])} with coords)")
        report_lines.append("\n")
        
        # פילוח לפי דחיפות
        report_lines.append("-" * 80)
        report_lines.append("BREAKDOWN BY URGENCY")
        report_lines.append("-" * 80)
        urgency_breakdown = self.sample['Report_Urgency'].value_counts()
        for urgency, count in urgency_breakdown.items():
            report_lines.append(f"{urgency}: {count} reports")
        report_lines.append("\n")
        
        # פילוח לפי דפוס חילוץ
        report_lines.append("-" * 80)
        report_lines.append("BREAKDOWN BY EXTRACTION PATTERN (for positive cases)")
        report_lines.append("-" * 80)
        pattern_breakdown = self.sample[self.sample['Has_Coordinate'] == 1]['Extraction_Pattern'].value_counts()
        for pattern, count in pattern_breakdown.items():
            report_lines.append(f"{pattern}: {count} matches")
        report_lines.append("\n")
        
        # Edge Case Analysis
        report_lines.append("-" * 80)
        report_lines.append("EDGE CASE ANALYSIS")
        report_lines.append("-" * 80)
        report_lines.append(f"Average edge score: {self.sample['edge_score'].mean():.2f}")
        report_lines.append(f"Max edge score: {self.sample['edge_score'].max():.0f}")
        report_lines.append(f"Min edge score: {self.sample['edge_score'].min():.0f}")
        report_lines.append("\nTop edge case reasons:")
        
        # ספירת סיבות (כל סיבה בנפרד)
        all_reasons = []
        for reasons_str in self.sample['edge_reasons']:
            if reasons_str:
                all_reasons.extend(reasons_str.split(', '))
        
        from collections import Counter
        reason_counts = Counter(all_reasons)
        for reason, count in reason_counts.most_common(10):
            report_lines.append(f"  - {reason}: {count} occurrences")
        report_lines.append("\n")
        
        # תוכן Sample Examples
        report_lines.append("-" * 80)
        report_lines.append("SAMPLE EXAMPLES (First 10)")
        report_lines.append("-" * 80)
        for idx, row in self.sample.head(10).iterrows():
            report_lines.append(f"\nReport ID: {row['Report_ID']}")
            report_lines.append(f"Has Coordinate: {'Yes' if row['Has_Coordinate'] == 1 else 'No'}")
            if row['Has_Coordinate'] == 1:
                report_lines.append(f"Extracted Coordinate: {row['Extracted_Coordinate']}")
            report_lines.append(f"Edge Score: {row['edge_score']:.0f}")
            report_lines.append(f"Edge Reasons: {row['edge_reasons']}")
            report_lines.append(f"Content: {row['Content_Body'][:100]}...")
            report_lines.append("-" * 40)
        
        # הוראות למתייג
        report_lines.append("\n")
        report_lines.append("=" * 80)
        report_lines.append("INSTRUCTIONS FOR TAGGERS")
        report_lines.append("הוראות למתייגים")
        report_lines.append("=" * 80)
        report_lines.append("\n**Column Descriptions:**")
        report_lines.append("- Extracted_Coordinate: What our model extracted (as STRING to preserve leading zeros)")
        report_lines.append("- Y_N_MODEL: Our model's decision (Yes/No)")
        report_lines.append("- Y_N_TAG: [FILL THIS] Your validation (Yes/No)")
        report_lines.append("- Tagged_Coordinate: [FILL THIS] The correct coordinate if exists")
        report_lines.append("- Is_Edge_Case: 'Yes' if this is a challenging case (pay extra attention!)")
        report_lines.append("- Edge_Case_Reason: Why this case is challenging (in Hebrew)")
        report_lines.append("")
        report_lines.append("**Tagging Instructions:**")
        report_lines.append("\n1. Review each report's Content_Body carefully")
        report_lines.append("2. Pay EXTRA attention to reports where Is_Edge_Case = 'Yes'")
        report_lines.append("3. Check if the model's extraction (Y_N_MODEL) is correct")
        report_lines.append("4. Fill in Y_N_TAG column:")
        report_lines.append("   - 'Yes' if there IS a valid coordinate")
        report_lines.append("   - 'No' if there is NO coordinate")
        report_lines.append("5. If Y_N_TAG = 'Yes', write the 6-digit coordinate in Tagged_Coordinate column")
        report_lines.append("6. Leave Tagged_Coordinate empty if Y_N_TAG = 'No'")
        report_lines.append("")
        report_lines.append("**Definition of valid coordinate:**")
        report_lines.append("- Exactly 6 digits")
        report_lines.append("- Associated with location anchor words (נ.צ, מיקום, נקודת ציון, etc.)")
        report_lines.append("- Represents an actual geographic coordinate")
        report_lines.append("- Write as STRING (preserve leading zeros if any, e.g., '012345')")
        report_lines.append("\n")
        report_lines.append("=" * 80)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 80)
        
        # שמירה
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"[OK] Tagging report saved to: {output_path}")


def main():
    """
    Main execution function
    """
    print("=" * 80)
    print("TAGGING SAMPLE GENERATOR - QA PIPELINE")
    print("שלב ד': יצירת מדגם תיוג")
    print("=" * 80)
    print()
    
    # הגדרת נתיבים
    input_file = Path('data/processed/reports_with_coordinates.csv')
    tagging_file = Path('data/tagging/tagging_task.csv')
    report_file = Path('outputs/reports/tagging_sample_report.txt')
    
    # בדיקת קיום קובץ קלט
    if not input_file.exists():
        print(f"[ERROR] Input file not found at {input_file}")
        print("Please run feature engineering (step 3) first.")
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
    
    # יצירת מחולל המדגם
    generator = TaggingSampleGenerator(df)
    
    # יצירת המדגם
    sample_df = generator.generate_sample()
    
    # יצירת קובץ תיוג
    tagging_df = generator.create_tagging_file(tagging_file)
    
    # יצירת דוח
    generator.generate_tagging_report(report_file)
    
    print()
    print("=" * 80)
    print("TAGGING SAMPLE GENERATION COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("Output Files:")
    print(f"  1. Tagging Task File: {tagging_file}")
    print(f"     → Send this file to human taggers")
    print(f"  2. Generation Report: {report_file}")
    print(f"     → Review the sample composition and statistics")
    print()
    print("Next Steps:")
    print("  1. Send tagging_task.csv to human taggers")
    print("  2. Wait for completed tagging")
    print("  3. Run performance evaluation (Step 5)")


if __name__ == "__main__":
    main()

