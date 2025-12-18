"""
Performance Visualizations Generator
=====================================
יצירת ויזואליזציות לדוח הערכת הביצועים

Creates professional charts and graphs for the performance evaluation report.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Import for Hebrew text support
try:
    from bidi.algorithm import get_display
    import arabic_reshaper
    HEBREW_SUPPORT = True
except ImportError:
    HEBREW_SUPPORT = False
    # Silent - Hebrew will just appear reversed in charts

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.unicode_minus'] = False


def fix_hebrew(text):
    """
    Fix Hebrew text direction for matplotlib
    """
    if not HEBREW_SUPPORT or not text:
        return text
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except:
        return text


class PerformanceVisualizer:
    """
    יוצר ויזואליזציות מקצועיות לדוח הביצועים
    """
    
    def __init__(self, tagged_file_path, output_dir='outputs/visualizations'):
        self.tagged_file = Path(tagged_file_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.df = None
        
        print("="*80)
        print("CREATING PERFORMANCE VISUALIZATIONS")
        print("יצירת ויזואליזציות ביצועים")
        print("="*80)
        print()
    
    def load_data(self):
        """טעינת נתונים"""
        print(f"Loading data from: {self.tagged_file}")
        
        encodings = ['utf-8-sig', 'utf-8', 'cp1255']
        for encoding in encodings:
            try:
                self.df = pd.read_csv(self.tagged_file, encoding=encoding)
                print(f"OK Loaded with encoding: {encoding}")
                break
            except:
                continue
        
        if self.df is None:
            raise ValueError("Could not load file")
        
        # Clean data
        self.df['Y_N_MODEL'] = self.df['Y_N_MODEL'].astype(str).str.strip().str.upper()
        self.df['Y_N_TAG'] = self.df['Y_N_TAG'].astype(str).str.strip().str.upper()
        
        valid_values = ['YES', 'NO']
        self.df = self.df[
            (self.df['Y_N_MODEL'].isin(valid_values)) & 
            (self.df['Y_N_TAG'].isin(valid_values))
        ].copy()
        
        print(f"Valid records: {len(self.df)}\n")
    
    def create_confusion_matrix_heatmap(self):
        """
        יצירת Confusion Matrix כ-Heatmap
        """
        print("Creating Confusion Matrix Heatmap...")
        
        # Calculate confusion matrix
        tp = len(self.df[(self.df['Y_N_MODEL'] == 'YES') & (self.df['Y_N_TAG'] == 'YES')])
        fp = len(self.df[(self.df['Y_N_MODEL'] == 'YES') & (self.df['Y_N_TAG'] == 'NO')])
        tn = len(self.df[(self.df['Y_N_MODEL'] == 'NO') & (self.df['Y_N_TAG'] == 'NO')])
        fn = len(self.df[(self.df['Y_N_MODEL'] == 'NO') & (self.df['Y_N_TAG'] == 'YES')])
        
        # Create matrix
        cm = np.array([[tp, fp], [fn, tn]])
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create heatmap
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Positive (Yes)', 'Negative (No)'],
                    yticklabels=['Positive (Yes)', 'Negative (No)'],
                    cbar_kws={'label': 'Count'},
                    annot_kws={'size': 16, 'weight': 'bold'},
                    linewidths=2, linecolor='black',
                    ax=ax)
        
        # Add labels
        ax.set_xlabel('Actual (Human Tag)', fontsize=14, weight='bold')
        ax.set_ylabel('Predicted (Model)', fontsize=14, weight='bold')
        title = 'Confusion Matrix - Coordinate Extraction Model\n' + fix_hebrew('מטריצת בילבול - מודל חילוץ נ.צ')
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        
        # Add annotations
        ax.text(0.5, 0.25, f'TP\n{tp}', ha='center', va='center', 
                fontsize=12, weight='bold', color='darkgreen')
        ax.text(1.5, 0.25, f'FP\n{fp}', ha='center', va='center', 
                fontsize=12, weight='bold', color='darkred')
        ax.text(0.5, 1.25, f'FN\n{fn}', ha='center', va='center', 
                fontsize=12, weight='bold', color='darkorange')
        ax.text(1.5, 1.25, f'TN\n{tn}', ha='center', va='center', 
                fontsize=12, weight='bold', color='darkgreen')
        
        plt.tight_layout()
        
        # Save
        output_file = self.output_dir / '07_confusion_matrix.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"OK Saved: {output_file}")
        plt.close()
    
    def create_metrics_bar_chart(self):
        """
        גרף עמודות של מדדי הביצועים
        """
        print("Creating Metrics Bar Chart...")
        
        # Calculate metrics
        tp = len(self.df[(self.df['Y_N_MODEL'] == 'YES') & (self.df['Y_N_TAG'] == 'YES')])
        fp = len(self.df[(self.df['Y_N_MODEL'] == 'YES') & (self.df['Y_N_TAG'] == 'NO')])
        tn = len(self.df[(self.df['Y_N_MODEL'] == 'NO') & (self.df['Y_N_TAG'] == 'NO')])
        fn = len(self.df[(self.df['Y_N_MODEL'] == 'NO') & (self.df['Y_N_TAG'] == 'YES')])
        
        total = tp + fp + tn + fn
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = (tp + tn) / total if total > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        # Create data
        metrics = ['Precision', 'Recall', 'F1-Score', 'Accuracy', 'Specificity']
        values = [precision, recall, f1_score, accuracy, specificity]
        colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c', '#f39c12']
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 7))
        
        bars = ax.bar(metrics, values, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{value:.1%}',
                    ha='center', va='bottom', fontsize=14, weight='bold')
        
        # Styling
        ax.set_ylabel('Score', fontsize=13, weight='bold')
        title = 'Performance Metrics - Coordinate Extraction Model\n' + fix_hebrew('מדדי ביצועים - מודל חילוץ נ.צ')
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        ax.set_ylim(0, 1.1)
        ax.axhline(y=0.85, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Good Threshold (85%)')
        ax.axhline(y=0.95, color='darkgreen', linestyle='--', linewidth=2, alpha=0.5, label='Excellent Threshold (95%)')
        ax.legend(loc='lower right', fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Save
        output_file = self.output_dir / '08_performance_metrics.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"OK Saved: {output_file}")
        plt.close()
    
    def create_sector_performance_chart(self):
        """
        ביצועים לפי מגזר - מפורט (TP/FP/FN)
        """
        print("Creating Sector Performance Chart...")
        
        if 'Sector' not in self.df.columns:
            print("Warning: Sector column not found - skipping")
            return
        
        sectors = []
        tps = []
        fps = []
        fns = []
        
        for sector in sorted(self.df['Sector'].unique()):
            sector_df = self.df[self.df['Sector'] == sector]
            
            tp = len(sector_df[(sector_df['Y_N_MODEL'] == 'YES') & (sector_df['Y_N_TAG'] == 'YES')])
            fp = len(sector_df[(sector_df['Y_N_MODEL'] == 'YES') & (sector_df['Y_N_TAG'] == 'NO')])
            fn = len(sector_df[(sector_df['Y_N_MODEL'] == 'NO') & (sector_df['Y_N_TAG'] == 'YES')])
            
            sectors.append(fix_hebrew(sector))
            tps.append(tp)
            fps.append(fp)
            fns.append(fn)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))
        
        x = np.arange(len(sectors))
        width = 0.25
        
        bars1 = ax.bar(x - width, tps, width, label='True Positive (Correct)', 
                       color='#2ecc71', alpha=0.8, edgecolor='black')
        bars2 = ax.bar(x, fps, width, label='False Positive (Wrong)', 
                       color='#e74c3c', alpha=0.8, edgecolor='black')
        bars3 = ax.bar(x + width, fns, width, label='False Negative (Missed)', 
                       color='#f39c12', alpha=0.8, edgecolor='black')
        
        # Add value labels
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                            f'{int(height)}',
                            ha='center', va='bottom', fontsize=10, weight='bold')
        
        ax.set_xlabel('Sector', fontsize=13, weight='bold')
        ax.set_ylabel('Count', fontsize=13, weight='bold')
        title = 'Model Performance by Sector\n' + fix_hebrew('ביצועי המודל לפי מגזר')
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(sectors, rotation=15, ha='right')
        ax.legend(fontsize=11, loc='upper right')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Save
        output_file = self.output_dir / '09_sector_performance.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"OK Saved: {output_file}")
        plt.close()
    
    def create_error_types_pie_chart(self):
        """
        התפלגות סוגי שגיאות
        """
        print("Creating Error Types Pie Chart...")
        
        tp = len(self.df[(self.df['Y_N_MODEL'] == 'YES') & (self.df['Y_N_TAG'] == 'YES')])
        fp = len(self.df[(self.df['Y_N_MODEL'] == 'YES') & (self.df['Y_N_TAG'] == 'NO')])
        tn = len(self.df[(self.df['Y_N_MODEL'] == 'NO') & (self.df['Y_N_TAG'] == 'NO')])
        fn = len(self.df[(self.df['Y_N_MODEL'] == 'NO') & (self.df['Y_N_TAG'] == 'YES')])
        
        # Create data
        labels = ['True Positive\n(Correct Yes)', 'True Negative\n(Correct No)', 
                  'False Positive\n(Wrong Yes)', 'False Negative\n(Missed)']
        sizes = [tp, tn, fp, fn]
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']
        explode = (0.05, 0.05, 0.1, 0.1)  # Emphasize errors
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 9))
        
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                            autopct='%1.1f%%', shadow=True, startangle=90,
                                            textprops={'fontsize': 12, 'weight': 'bold'})
        
        # Enhance percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(13)
            autotext.set_weight('bold')
        
        # Add counts
        for i, (label, size) in enumerate(zip(labels, sizes)):
            angle = (wedges[i].theta2 + wedges[i].theta1) / 2
            x = np.cos(np.radians(angle)) * 1.3
            y = np.sin(np.radians(angle)) * 1.3
            ax.text(x, y, f'n={size}', ha='center', va='center',
                    fontsize=11, weight='bold', 
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        title = 'Prediction Results Distribution\n' + fix_hebrew('התפלגות תוצאות החיזוי')
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        
        plt.tight_layout()
        
        # Save
        output_file = self.output_dir / '10_prediction_distribution.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"OK Saved: {output_file}")
        plt.close()
    
    def create_urgency_comparison(self):
        """
        השוואת ביצועים לפי דחיפות
        """
        print("Creating Urgency Comparison Chart...")
        
        if 'Report_Urgency' not in self.df.columns:
            print("⚠️ Report_Urgency column not found - skipping")
            return
        
        urgencies = []
        tps = []
        fps = []
        fns = []
        
        for urgency in sorted(self.df['Report_Urgency'].unique()):
            urgency_df = self.df[self.df['Report_Urgency'] == urgency]
            
            tp = len(urgency_df[(urgency_df['Y_N_MODEL'] == 'YES') & (urgency_df['Y_N_TAG'] == 'YES')])
            fp = len(urgency_df[(urgency_df['Y_N_MODEL'] == 'YES') & (urgency_df['Y_N_TAG'] == 'NO')])
            fn = len(urgency_df[(urgency_df['Y_N_MODEL'] == 'NO') & (urgency_df['Y_N_TAG'] == 'YES')])
            
            urgencies.append(fix_hebrew(urgency))
            tps.append(tp)
            fps.append(fp)
            fns.append(fn)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 7))
        
        x = np.arange(len(urgencies))
        width = 0.25
        
        bars1 = ax.bar(x - width, tps, width, label='True Positive (Correct)', 
                       color='#2ecc71', alpha=0.8, edgecolor='black')
        bars2 = ax.bar(x, fps, width, label='False Positive (Wrong)', 
                       color='#e74c3c', alpha=0.8, edgecolor='black')
        bars3 = ax.bar(x + width, fns, width, label='False Negative (Missed)', 
                       color='#f39c12', alpha=0.8, edgecolor='black')
        
        # Add value labels
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                            f'{int(height)}',
                            ha='center', va='bottom', fontsize=10, weight='bold')
        
        ax.set_xlabel('Urgency Level', fontsize=13, weight='bold')
        ax.set_ylabel('Count', fontsize=13, weight='bold')
        title = 'Model Performance by Urgency Level\n' + fix_hebrew('ביצועי המודל לפי רמת דחיפות')
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(urgencies, rotation=15, ha='right')
        ax.legend(fontsize=11, loc='upper right')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Save
        output_file = self.output_dir / '11_urgency_comparison.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"OK Saved: {output_file}")
        plt.close()
    
    def generate_all_visualizations(self):
        """
        יצירת כל הויזואליזציות
        """
        self.load_data()
        
        print("Generating visualizations...\n")
        
        self.create_confusion_matrix_heatmap()
        self.create_metrics_bar_chart()
        self.create_sector_performance_chart()
        self.create_error_types_pie_chart()
        self.create_urgency_comparison()
        
        print("\n" + "="*80)
        print("SUCCESS - ALL VISUALIZATIONS CREATED!")
        print("="*80)
        print(f"\nOutput directory: {self.output_dir}")
        print("\nCreated files:")
        for i, name in enumerate(['07_confusion_matrix.png', 
                                   '08_performance_metrics.png',
                                   '09_sector_performance.png',
                                   '10_prediction_distribution.png',
                                   '11_urgency_comparison.png'], 1):
            print(f"  {i}. {name}")
        print()


def main():
    """נקודת כניסה"""
    # Find tagged file
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
        return
    
    # Create visualizations
    visualizer = PerformanceVisualizer(tagged_file)
    visualizer.generate_all_visualizations()


if __name__ == '__main__':
    main()

