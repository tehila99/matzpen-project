# -*- coding: utf-8 -*-
"""
Scan for all anchor words and coordinate patterns in the data
"""
import pandas as pd
import re
from collections import Counter

# Load data
df = pd.read_csv('data/processed/clean_reports.csv')

print('='*70)
print('Scanning for geographic anchor words in data')
print('='*70)

# Find all instances of 6 digits
coordinate_pattern = r'\d{6}'
anchor_contexts = []
coordinate_matches = 0

for idx, row in df.iterrows():
    content = str(row['Content_Body'])
    matches = re.finditer(coordinate_pattern, content)
    
    for match in matches:
        coordinate_matches += 1
        # Get 30 characters before the coordinate
        start = max(0, match.start() - 30)
        end = match.start()
        context_before = content[start:end]
        anchor_contexts.append(context_before)

print(f'\nFound {coordinate_matches} instances of 6-digit numbers')
print(f'In {len(df)} total reports')
print(f'\nSample contexts before coordinates (first 30):')
print('-'*70)
for i, ctx in enumerate(anchor_contexts[:30]):
    print(f'{i+1}. ...{ctx}<COORDINATE>')

# Search for specific anchor words
anchor_words = {
    'נ.צ.': 0,
    'נ.צ': 0,
    'נ צ': 0,
    'נקודת ציון': 0,
    'נק״צ': 0,
    'נק׳צ': 0,
    'מיקום': 0,
    'קואורדינטות': 0,
    'קורדינטות': 0,
    'נקודה': 0,
    'משבצת': 0,
    'רשת': 0,
    'GPS': 0,
    'קו רוחב': 0,
    'קו אורך': 0,
    'צפון': 0,
    'מזרח': 0,
}

print('\n' + '='*70)
print('Checking common anchor words:')
print('='*70)

for word in anchor_words.keys():
    count = df['Content_Body'].str.contains(word, na=False, case=False, regex=False).sum()
    anchor_words[word] = count
    if count > 0:
        print(f'{word:20s} : {count:5d} reports')

# Find words that appear near 6-digit numbers
print('\n' + '='*70)
print('Most common words before 6-digit numbers:')
print('='*70)

# Extract all words before coordinates
words_before_coords = []
for ctx in anchor_contexts:
    # Split by spaces and get last few words
    words = ctx.split()
    if words:
        # Get last 1-3 words
        words_before_coords.extend(words[-3:])

word_counter = Counter(words_before_coords)
print('\nTop 20 most common words before coordinates:')
for word, count in word_counter.most_common(20):
    print(f'{word:20s} : {count:5d} times')

# Save to file
with open('outputs/reports/anchor_words_analysis.txt', 'w', encoding='utf-8') as f:
    f.write('Anchor Words Analysis\n')
    f.write('='*70 + '\n\n')
    f.write(f'Total 6-digit patterns found: {coordinate_matches}\n')
    f.write(f'Total reports: {len(df)}\n\n')
    
    f.write('Anchor word frequencies:\n')
    f.write('-'*70 + '\n')
    for word, count in sorted(anchor_words.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            f.write(f'{word:20s} : {count:5d} reports\n')
    
    f.write('\n\nTop words before coordinates:\n')
    f.write('-'*70 + '\n')
    for word, count in word_counter.most_common(30):
        f.write(f'{word:20s} : {count:5d} times\n')
    
    f.write('\n\nSample contexts (first 50):\n')
    f.write('-'*70 + '\n')
    for i, ctx in enumerate(anchor_contexts[:50]):
        f.write(f'{i+1}. ...{ctx}<COORDINATE>\n')

print('\n\nAnalysis saved to: outputs/reports/anchor_words_analysis.txt')

