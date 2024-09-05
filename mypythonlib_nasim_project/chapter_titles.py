#!/usr/bin/env python3
import os
import re
import sys
import spacy

# Load the SpaCy model
nlp = spacy.load('fr_core_news_lg')

# Function to extract and clean chapter titles from the Table of Contents
def extract_chapter_titles_from_toc(text):
    toc_start = text.find('Table des matières')
    if toc_start == -1:
        toc_start = text.find('Table of Contents')
    
    if toc_start == -1:
        return None
    
    lines = text.splitlines()
    toc_lines = []
    in_toc = False

    # Process lines to extract the TOC
    for i, line in enumerate(lines):
        if 'Table des matières' in line or 'Table of Contents' in line:
            in_toc = True
            continue

        if in_toc:
            stripped_line = line.strip()

            # Stop when we encounter an empty line followed by another empty line (end of TOC)
            if stripped_line == '' and i + 1 < len(lines) and lines[i + 1].strip() == '':
                break

            if stripped_line and re.search(r'\d+$', stripped_line):  # Ensure the line ends with a number
                toc_lines.append(stripped_line)

    # Now process the collected TOC lines
    chapter_titles = {}
    for line in toc_lines:
        # Separate the title from the page number
        title = re.sub(r'\s*\d+\s*$', '', line).strip()

        # Store only titles that are not known to be non-TOC content
        if title and not re.search(r'achevé d’imprimer|composé', title, re.IGNORECASE):
            chapter_titles[title.lower()] = title  # Store the title in lowercase for case-insensitive matching

    # Verify chapter titles against the text to ensure they appear at the start of paragraphs
    validated_titles = {}
    for title in chapter_titles.keys():
        title_found = False
        for i, line in enumerate(lines):
            # Check if title matches after stripping and ignoring case
            current_line_cleaned = re.sub(r'[^\w\s]', '', line.strip().lower())  # Remove punctuation for comparison
            if i > 0 and lines[i - 1].strip() == '' and current_line_cleaned == title:
                title_found = True
                print(f"Title '{chapter_titles[title]}' found at the start of a paragraph.")
                break
            if i > 1 and lines[i - 2].strip() == '' and current_line_cleaned == title:
                title_found = True
                print(f"Title '{chapter_titles[title]}' found as the second line of a paragraph.")
                break

        if title_found:
            validated_titles[chapter_titles[title]] = chapter_titles[title]
        else:
            print(f"Title '{chapter_titles[title]}' from TOC not found at the start of a paragraph.")

    return validated_titles if validated_titles else None

# Function to detect chapter titles based on format
def extract_chapter_titles_by_format(text):
    chapter_titles = {}
    lines = text.splitlines()

    for i in range(1, len(lines) - 1):
        previous_line = lines[i - 1].strip()
        current_line = lines[i].strip()
        next_line = lines[i + 1].strip()

        # Exclude standalone numbers and short text fragments
        if (
            previous_line == '' and
            current_line and
            len(current_line.split()) > 1 and  # Ensure more than one word
            current_line[0].isupper() and
            not re.search(r'^\d+$', current_line) and  # Exclude standalone numbers
            not re.search(r'[.;:]$', current_line) and
            '»' not in current_line and
            re.match(r'^[A-Z]', current_line)  # Ensure the line starts with a capital letter
        ):
            if next_line and next_line[0].isupper():
                title = current_line.strip()
                chapter_titles[title] = title
    
    return chapter_titles

# Function to extract chapter titles (main function)
def extract_chapter_titles(text):
    chapter_titles = extract_chapter_titles_from_toc(text)
    
    if chapter_titles:
        return chapter_titles
    
    return extract_chapter_titles_by_format(text)

# Function to process a single text file
def process_text_file(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    chapter_titles = extract_chapter_titles(text)
    
    if chapter_titles:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            for title in chapter_titles.values():
                file.write(f'"{title}"\n')
        print(f"Extracted titles saved to {output_file_path}")
    else:
        print(f"No chapter titles found in {input_file_path}")

# Function to process all text files in a directory
def process_directory(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for file_name in os.listdir(input_directory):
        if file_name.endswith('.txt'):
            input_file_path = os.path.join(input_directory, file_name)
            output_file_path = os.path.join(output_directory, f'titles_{os.path.splitext(file_name)[0]}.txt')

            print(f"Processing {file_name}...")
            process_text_file(input_file_path, output_file_path)
            print(f"Processed file saved as {output_file_path}")

# Main script execution
if __name__ == "__main__":
    input_directory = os.path.join("../", "txt_processed/1-page_nb_cln")
    output_directory = os.path.join("../", "txt_processed/11-chapter_titles")

    process_directory(input_directory, output_directory)
    print("Script completed")
