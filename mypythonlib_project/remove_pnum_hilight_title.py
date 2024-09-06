#!/usr/bin/env python3
import os
import re
import unicodedata
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

        # Replace spaces with a pattern that allows for line breaks, varying whitespace, and hyphens
        flexible_title = re.escape(normalized_title).replace(r'\ ', r'[\s\-]*')

        # Create the regex pattern to match the title with possible line breaks and hyphens
        title_pattern = re.compile(r'(^' + flexible_title + r')', re.MULTILINE | re.IGNORECASE)

        # Only mark the title if it hasn't been marked yet
        if normalized_title not in marked_titles:
            new_title = r'@@ \1 @@'
            normalized_text, count = title_pattern.subn(new_title, normalized_text, count=1)  # Mark only once
            if count > 0:
                log_entries.append(f"Added markers to title: {normalized_title}, Occurrences: {count}")
                marked_titles.add(normalized_title)
            else:
                log_entries.append(f"Title not found in text: {normalized_title}")

    return normalized_text, log_entries

# Function to merge chapter titles that span more than two lines
def merge_split_titles(text):
    log_entries = []
    merged_text = []

    # Split the text into lines for processing
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this line contains the start of a marked chapter title (with @@)
        if line.startswith('@@') and i + 2 < len(lines):  # Ensure at least two more lines
            next_line = lines[i + 1].strip()
            third_line = lines[i + 2].strip()

            # If the second line is not empty, check if the third line should be merged
            if next_line and third_line and third_line.endswith('@@'):
                # Merge the third line into the second line
                lines[i + 1] = next_line + ' ' + third_line
                log_entries.append(f"Merged third line into second for title starting with: {line}")
                # Skip the third line since it was merged
                i += 2
            else:
                merged_text.append(line)
        else:
            merged_text.append(line)

        i += 1

    # Re-join the text lines after processing
    merged_text = '\n'.join(merged_text)

    return merged_text, log_entries

# Function to remove phrases at the start or end of paragraphs, even if split across lines
def remove_phrase_at_paragraph_start_or_end(text, phrases):
    log_entries = []

    for phrase in phrases:
        if re.match(r'^\W*-\w+\W*$', phrase) or phrase.strip() == ',':
            log_entries.append(f"Skipped removing phrase due to exception: {phrase}")
            continue

        phrase_pattern = re.compile(r'(\n\s*' + re.escape(phrase.replace('\n', ' ')) + r'\s*\n)', re.IGNORECASE)
        start_pattern = re.compile(r'(^\s*' + re.escape(phrase.replace('\n', ' ')) + r'\s*$)', re.IGNORECASE)
        end_pattern = re.compile(r'(^\s*' + re.escape(phrase.replace('\n', ' ')) + r'\s*$)', re.IGNORECASE)

        text, count = phrase_pattern.subn('\n\n', text)
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

    number_pattern = re.compile(r'(\n\s*)(\d{1,5})(\s*\n)')

    def first_pass_replace(match):
        number = int(match.group(2))
        if 0 <= number <= 10000 and (not first_pass_removed or number <= max(first_pass_removed) + 20):
            first_pass_removed.add(number)
            removed_numbers[number] += 1
            return match.group(1) + '\n\n'
        return match.group(0)

    cleaned_text = number_pattern.sub(first_pass_replace, text)

    if first_pass_removed:
        min_removed = min(first_pass_removed)
        max_removed = max(first_pass_removed)

        def second_pass_replace(match):
            number = int(match.group(2))
            if min_removed <= number <= max_removed and number not in first_pass_removed and number not in second_pass_removed:
                second_pass_removed.add(number)
                removed_numbers[number] += 1
                return match.group(1) + '\n\n'
            return match.group(0)

        cleaned_text = number_pattern.sub(second_pass_replace, cleaned_text)

    for number, count in removed_numbers.items():
        log_entries.append(f"Removed page number: {number} (removed {count} time(s)).")

    return cleaned_text, log_entries

# Function to identify and remove recurring patterns
def identify_and_remove_recurring_patterns(text, log_entries):
    paragraphs = [para.strip() for para in re.split(r'\n{2,}', text) if para.strip()]

    def find_recurring_phrases(paragraphs):
        phrase_counts = collections.defaultdict(int)
        for para in paragraphs:
            first_line = para.splitlines()[0].strip()
            if first_line:
                phrase_counts[first_line] += 1

            last_line = para.splitlines()[-1].strip()
            if last_line:
                phrase_counts[last_line] += 1

        recurring_phrases = {phrase for phrase, count in phrase_counts.items() if count >= 8}
        return recurring_phrases

    recurring_phrases = find_recurring_phrases(paragraphs)

    for phrase in recurring_phrases:
        if re.match(r'^\W*-\w+\W*$', phrase) or phrase.strip() == ',':
            log_entries.append(f"Skipped removing recurring phrase due to exception: {phrase}")
            continue

        if phrase.strip().upper() == '':
            log_entries.append(f"Skipped removing recurring phrase due to exception: {phrase}")
            continue

        log_entries.append(f"Identified recurring phrase: {phrase}")

        if re.match(r'^\d+$', phrase) or "mep_enleve_la_nuit.indd" in phrase:
            pattern = rf'(?<=\n)\s*{re.escape(phrase)}\s*(?=\n)|^\s*{re.escape(phrase)}\s*(?=\n|$)'
        else:
            pattern = rf'(?<=\n)\s*{re.escape(phrase)}\s*(?=\n)|^\s*{re.escape(phrase)}\s*(?=\n|$)'

        text, count = re.subn(pattern, '', text, flags=re.MULTILINE)

        if count > 0:
            log_entries.append(f"Removed recurring phrase: {phrase}, Occurrences: {count}")

    mep_pattern = re.compile(r'mep_enleve_la_nuit\.indd\s*\d+', re.IGNORECASE)
    text, mep_count = mep_pattern.subn('', text)
    if mep_count > 0:
        log_entries.append(f"Removed 'mep_enleve_la_nuit.indd' occurrences: {mep_count}")

    return text

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

    # Merge chapter titles split across more than two lines
    merged_text, merge_log_entries = merge_split_titles(highlighted_text)
    log_entries.extend(merge_log_entries)

    # Remove phrases at the start or end of paragraphs
    cleaned_text, phrase_log_entries = remove_phrase_at_paragraph_start_or_end(merged_text, phrases)
    log_entries.extend(phrase_log_entries)

    # Remove page numbers based on the specified rules
    cleaned_text, number_log_entries = remove_page_numbers(cleaned_text)
    log_entries.extend(number_log_entries)

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
        # Add your specific phrases here
    ]

    titles = [
    # "Introduction",
    # "chapitre 1 L’attachement premier et le sentiment de sécurité",
    # "1.2 Les besoins narcissiques et les premières communications",
    # "2 Les manifestations et les conséquences de l’abandon",
    # "2.2 Les frustrations et l’humeur triste",
    # "2.3 L’angoisse d’abandon de l’enfant adopté",
    # "2.4 La déprime des enfants et des adolescents",
    # "2.5 Le préjugé envers les petits garçons",
    # "2.6 Le déficit d’attention et l’hyperactivité",
    # "2.7 Le besoin de présence des enfants et l’individualisme des adultes",
    # "chapitre 3 Les apprentissages thérapeutiques et réparateurs",
    # "3.2 Le thérapeute, objet de transition et de transfert",
    # "3.3 La thérapie corrective avec les enfants",
    # "3.4 La thérapie à l’âge de la puberté",
    # "chapitre 4 Les apprentissages créatifs et régénérateurs",
    # "4.2 La thérapie par le rêve et la thérapie par l’écriture",
    # "4.3 Le langage de la création et de l’artiste",
    # "4.4 Les langages de l’émotion et l’intelligence du corps",
    # "4.5 L’environnement non humain",
    # "Conclusion",
    # "Glossaire",
    # "Bibliographie",
    # "Note de l’auteure"
    ]

    process_directory(input_directory, output_directory, log_directory, phrases, titles)
