#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import re
from translations import TRANSLATIONS

def should_not_translate(text):
    """Check if text should not be translated"""
    if not text or text.strip() == "":
        return True

    # Check if it's a URL
    if text.startswith(('http://', 'https://', 'www.', 'ftp://')):
        return True

    # Check if it's already Arabic
    arabic_chars = len([c for c in text if '\u0600' <= c <= '\u06FF'])
    if arabic_chars > len(text) * 0.3:  # More than 30% Arabic characters
        return True

    # Check if it's a code snippet or variable name
    if re.match(r'^[a-z_][a-z0-9_]*$', text, re.IGNORECASE):
        if '_' in text or (text.islower() or text.isupper()):
            return True

    # Check if it's a number only
    if text.replace('.', '').replace(',', '').replace(' ', '').isdigit():
        return True

    # Check if it's a date format
    date_patterns = [
        r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}',
        r'\d{1,2}:\d{2}',
        r'[A-Z]{2,3}\s+\d{1,2}',
    ]
    for pattern in date_patterns:
        if re.search(pattern, text):
            return True

    return False

def translate_text(text):
    """Translate English text to Arabic"""
    if should_not_translate(text):
        return text

    # Check direct translation
    if text in TRANSLATIONS:
        return TRANSLATIONS[text]

    # Check case-insensitive
    text_lower = text.lower()
    for key, value in TRANSLATIONS.items():
        if key.lower() == text_lower:
            return value

    # If contains parentheses, try to translate parts
    if '(' in text and ')' in text:
        parts = re.split(r'([()])', text)
        translated_parts = []
        for part in parts:
            if part in ('(', ')'):
                translated_parts.append(part)
            else:
                translated_parts.append(translate_text(part.strip()))
        return ''.join(translated_parts)

    # If contains brackets, try to translate parts
    if '[' in text and ']' in text:
        parts = re.split(r'([\[\]])', text)
        translated_parts = []
        for part in parts:
            if part in ('[', ']'):
                translated_parts.append(part)
            else:
                translated_parts.append(translate_text(part.strip()))
        return ''.join(translated_parts)

    # Try to handle compound phrases
    # Check for "X and Y" pattern
    if ' and ' in text_lower:
        parts = text.split(' and ')
        if len(parts) == 2:
            part1 = translate_text(parts[0].strip())
            part2 = translate_text(parts[1].strip())
            return f"{part1} و {part2}"

    # Check for "X or Y" pattern
    if ' or ' in text_lower:
        parts = text.split(' or ')
        if len(parts) == 2:
            part1 = translate_text(parts[0].strip())
            part2 = translate_text(parts[1].strip())
            return f"{part1} أو {part2}"

    # Check for possessive patterns "X's Y"
    if "'s " in text:
        parts = text.split("'s ", 1)
        if len(parts) == 2:
            owner = translate_text(parts[0].strip())
            owned = translate_text(parts[1].strip())
            return f"{owned} {owner}"

    # If still no translation, return original
    return text

def split_and_translate_csv():
    """Split CSV into 2 files and translate each"""
    input_file = '/home/user/email-notification-templates/export-language.csv'
    output_file1 = '/home/user/email-notification-templates/export-language-part1.csv'
    output_file2 = '/home/user/email-notification-templates/export-language-part2.csv'

    # Read all rows
    all_rows = []
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            all_rows.append(row)

    total_rows = len(all_rows)
    mid_point = total_rows // 2

    print(f"Total rows: {total_rows}")
    print(f"Splitting at row: {mid_point}")

    # Process and write first half
    print("\nProcessing part 1...")
    with open(output_file1, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)

        for i, row in enumerate(all_rows[:mid_point]):
            if len(row) >= 2:
                english_text = row[0]
                arabic_text = translate_text(english_text)
                row[1] = arabic_text
            writer.writerow(row)
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{mid_point} rows")

    print(f"✓ Part 1 completed: {mid_point} rows")

    # Process and write second half
    print("\nProcessing part 2...")
    with open(output_file2, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)

        for i, row in enumerate(all_rows[mid_point:]):
            if len(row) >= 2:
                english_text = row[0]
                arabic_text = translate_text(english_text)
                row[1] = arabic_text
            writer.writerow(row)
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{total_rows - mid_point} rows")

    print(f"✓ Part 2 completed: {total_rows - mid_point} rows")
    print(f"\nDone! Created:")
    print(f"  - {output_file1}")
    print(f"  - {output_file2}")

if __name__ == '__main__':
    split_and_translate_csv()
