#!/usr/bin/env python3
import os
import re
import unicodedata
import sys
import collections

# Function to highlight chapter titles
def highlight_titles(text, titles):
    log_entries = []
    marked_titles = set()

    # Normalize text to ensure consistency in accent handling
    normalized_text = unicodedata.normalize('NFC', text)

    for title in titles:
        # Normalize the title
        normalized_title = unicodedata.normalize('NFC', title)

        # Split the title into chapter and title parts
        parts = normalized_title.split(' ', 2)
        chapter = ' '.join(parts[:2])
        chapter_title = parts[2] if len(parts) > 2 else ''

        # Ensure the pattern matches the chapter title format with possible line breaks, varying whitespace, and optional punctuation
        title_pattern = re.compile(r'(^' + re.escape(chapter) + r'[\s\S]*?' + re.escape(chapter_title) + r')', re.MULTILINE)
        alt_title_pattern = re.compile(r'(^' + re.escape(chapter) + r'[\s\S]+?' + re.escape(chapter_title) + r')', re.MULTILINE)

        # Only mark the title if it hasn't been marked yet
        if normalized_title not in marked_titles:
            new_title = r'@@ \1 @@'
            normalized_text, count = title_pattern.subn(new_title, normalized_text, count=1)  # Mark only once
            if count == 0:
                normalized_text, count = alt_title_pattern.subn(new_title, normalized_text, count=1)  # Mark only once
            if count > 0:
                log_entries.append(f"Added markers to title: {normalized_title}, Occurrences: {count}")
                marked_titles.add(normalized_title)
            else:
                log_entries.append(f"Title not found in text: {normalized_title}")

    return normalized_text, log_entries

# Function to remove phrases at the start or end of paragraphs, even if split across lines
def remove_phrase_at_paragraph_start_or_end(text, phrases):
    log_entries = []

    for phrase in phrases:
        # Escape the phrase and handle potential line breaks or punctuation
        phrase_pattern = re.compile(r'(\n\s*' + re.escape(phrase.replace('\n', ' ')) + r'\s*\n)', re.IGNORECASE)
        start_pattern = re.compile(r'(^\s*' + re.escape(phrase.replace('\n', ' ')) + r'\s*$)', re.IGNORECASE)
        end_pattern = re.compile(r'(^\s*' + re.escape(phrase.replace('\n', ' ')) + r'\s*$)', re.IGNORECASE)

        # Replace the phrases in the text
        text, count = phrase_pattern.subn('\n\n', text)  # Add paragraph break after removal
        text, start_count = start_pattern.subn('', text)
        text, end_count = end_pattern.subn('', text)

        total_count = count + start_count + end_count
        if total_count > 0:
            log_entries.append(f"Removed phrase: {phrase}, Total Occurrences: {total_count}")

    return text, log_entries

# Function to remove page numbers based on the rules provided
def remove_page_numbers(text):
    log_entries = []
    first_pass_removed = set()
    second_pass_removed = set()
    removed_numbers = collections.defaultdict(int)

    # Pattern to match numbers at the end of paragraphs with no text before or after them
    number_pattern = re.compile(r'(\n\s*)(\d{1,5})(\s*\n)')

    # First scan: Remove numbers at the end of paragraphs within the 0 to 10,000 range
    def first_pass_replace(match):
        number = int(match.group(2))
        if 0 <= number <= 10000 and (not first_pass_removed or number <= max(first_pass_removed) + 20):
            first_pass_removed.add(number)
            removed_numbers[number] += 1
            return match.group(1) + '\n\n'  # Preserve paragraph break after removing the number
        return match.group(0)

    cleaned_text = number_pattern.sub(first_pass_replace, text)

    # Second scan: Remove remaining numbers within the first and last removed range
    if first_pass_removed:
        min_removed = min(first_pass_removed)
        max_removed = max(first_pass_removed)

        def second_pass_replace(match):
            number = int(match.group(2))
            if min_removed <= number <= max_removed and number not in first_pass_removed and number not in second_pass_removed:
                second_pass_removed.add(number)
                removed_numbers[number] += 1
                return match.group(1) + '\n\n'  # Preserve paragraph break after removing the number
            return match.group(0)

        cleaned_text = number_pattern.sub(second_pass_replace, cleaned_text)

    # Log all removed numbers and their counts
    for number, count in removed_numbers.items():
        log_entries.append(f"Removed page number: {number} (removed {count} time(s)).")

    return cleaned_text, log_entries

# Function to identify and remove recurring patterns
def identify_and_remove_recurring_patterns(text, log_entries):
    # Split text into paragraphs
    paragraphs = [para.strip() for para in re.split(r'\n{2,}', text) if para.strip()]

    # Debug: Print the number of paragraphs and sample paragraphs
    print(f"Number of paragraphs: {len(paragraphs)}")
    for i, para in enumerate(paragraphs[:5]):  # Print first 5 paragraphs
        print(f"Paragraph {i+1}: {para[:100]}...")  # Print first 100 characters

    # Find recurring phrases
    def find_recurring_phrases(paragraphs):
        text_combined = '\n'.join(paragraphs)
        counts = collections.Counter(text_combined.split('\n'))
        recurring_phrases = {phrase for phrase, count in counts.items() if count >= 8}
        
        # Debug: Print found recurring phrases
        print(f"Found recurring phrases: {recurring_phrases}")
        return recurring_phrases

    recurring_phrases = find_recurring_phrases(paragraphs)

    # Debug: Print the recurring phrases that will be removed
    print(f"Recurring phrases to be removed: {recurring_phrases}")

    # Regex patterns to handle different cases
    for phrase in recurring_phrases:
        # Log the identified recurring phrase
        log_entries.append(f"Identified recurring phrase: {phrase}")
        
        # Handle standalone page numbers
        if re.match(r'^\d+$', phrase):
            pattern = rf'(?<=\n)\s*{re.escape(phrase)}\s*(?=\n)|^\s*{re.escape(phrase)}\s*(?=\n|$)'
        else:
            # Create regex pattern to match the phrase at the beginning or end of paragraphs
            pattern = rf'(?<=\n)\s*{re.escape(phrase)}\s*(?=\n)|^\s*{re.escape(phrase)}\s*(?=\n|$)'
        
        # Debug: Print the regex pattern
        print(f"Regex pattern: {pattern}")
        
        # Remove the recurring phrase from the text and count the number of removals
        text, count = re.subn(pattern, '', text, flags=re.MULTILINE)
        
        # Log the removal of the phrase and how many times it was removed
        if count > 0:
            log_entries.append(f"Removed recurring phrase: {phrase}, Occurrences: {count}")

    return text

# Example usage
log_entries = []
sample_text = """Your sample text here"""
processed_text = identify_and_remove_recurring_patterns(sample_text, log_entries)

# Print log entries for review
print("\nLog entries:")
for entry in log_entries:
    print(entry)

# Function to remove standalone periods or lines with only dots
def remove_standalone_dots(text):
    log_entries = []
    # Pattern to match standalone periods or lines with multiple dots with no other text
    dot_pattern = re.compile(r'^\s*(\.\s*)+$', re.MULTILINE)
    cleaned_text, count = dot_pattern.subn('', text)
    if count > 0:
        log_entries.append(f"Removed {count} lines with standalone periods or dots.")
    return cleaned_text, log_entries

# Function to process a single text file
def process_text_file(input_file_path, output_file_path, log_file_path, phrases, titles):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    log_entries = []

    # Identify and remove recurring patterns
    text = identify_and_remove_recurring_patterns(text, log_entries)

    # Highlight titles
    highlighted_text, title_log_entries = highlight_titles(text, titles)
    log_entries.extend(title_log_entries)

    # Remove phrases at the start or end of paragraphs
    cleaned_text, phrase_log_entries = remove_phrase_at_paragraph_start_or_end(highlighted_text, phrases)
    log_entries.extend(phrase_log_entries)

    # Remove page numbers based on the specified rules
    cleaned_text, number_log_entries = remove_page_numbers(cleaned_text)
    log_entries.extend(number_log_entries)

    # Remove standalone periods or lines with only dots
    cleaned_text, dot_log_entries = remove_standalone_dots(cleaned_text)
    log_entries.extend(dot_log_entries)

    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_text)

    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write("\n".join(log_entries))

# Function to process all text files in a directory
def process_directory(input_directory, output_directory, log_directory, phrases, titles):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    for file_name in os.listdir(input_directory):
        if file_name.endswith('.txt'):
            input_file_path = os.path.join(input_directory, file_name)
            output_file_path = os.path.join(output_directory, file_name)
            log_file_path = os.path.join(log_directory, f'log_{os.path.splitext(file_name)[0]}.txt')

            print(f"Processing {file_name}...")
            process_text_file(input_file_path, output_file_path, log_file_path, phrases, titles)
            print(f"Processed file saved as {output_file_path}")

if __name__ == "__main__":
    input_directory = os.path.join("../", "txt_processed/0-main_txt")
    output_directory = os.path.join("../", "txt_processed/1-page_nb_cln")
    log_directory = os.path.join(output_directory, "logs")
    
    # Define the phrases and titles
    phrases = [
        "fdsfd"
    ]
    titles = [
        "Chapitre 1"
    ]

    process_directory(input_directory, output_directory, log_directory, phrases, titles)
