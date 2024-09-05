#!/usr/bin/env python3
import os
import re
import spacy
import logging
import sys

# Add the base directory to the PYTHONPATH
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Load the SpaCy French large model
try:
    nlp = spacy.load("fr_core_news_lg")
except Exception as e:
    logging.error(f"Error loading SpaCy model: {e}")
    raise

# Define the input and output directories
input_dir = os.path.join(base_dir, 'txt_processed/4-numbers_replaced')
output_dir = os.path.join(base_dir, 'txt_processed/5-line-fix')
logs_dir = os.path.join(output_dir, 'logs')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Function to add break times after titles
def add_break_times(text):
    lines = text.splitlines()
    new_lines = []

    # Add break time of 0.5 seconds at the beginning
    new_lines.append('<break time="0.8s" />')

    # Iterate through lines and add the break time after the title on the second line
    for i, line in enumerate(lines):
        new_lines.append(line)
        if i == 1:  # Assuming the title is on the second line (index 1)
            new_lines[-1] = new_lines[-1] + " <break time=\"2.0s\" />"

    # Ensure the text ends with a break
    new_lines.append('<break time="2.8s" />')

    return "\n".join(new_lines)

# Function to check if a word is valid using SpaCy
def is_valid_word(word):
    doc = nlp(word)
    return len(doc) == 1 and doc[0].is_alpha

# Function to remove hyphens that break words at the end of lines
def fix_broken_hyphens(text):
    corrected_text = []
    changes = []

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.endswith('-') and i + 1 < len(lines):
            next_line = lines[i + 1].lstrip()
            last_word = line.split()[-1]
            parts = last_word.split('-')
            if len(parts) == 2:
                before, after = parts
                combined_word = before + after
                # Updated condition to ensure the next line does not start with a capital letter or the word is not a proper noun
                if is_valid_word(combined_word) and after.islower() and not next_line[0].isupper():
                    changes.append(f"Removed hyphen in: {last_word} -> {combined_word}")
                    # Remove the hyphen and merge the lines correctly
                    line = line[:-len(last_word)] + combined_word + next_line[len(after):].lstrip()
                    i += 1  # Skip the next line as it has been merged
        corrected_text.append(line)
        i += 1

    text = '\n'.join(corrected_text)

    # Ensure proper merging of broken words without adding extra spaces, avoiding merging names followed by lowercase letters
    text = re.sub(r'([a-zàâçéèêëîïôûùüÿñæœ,;])-\s*\n\s*(?![A-Z])([a-zàâçéèêëîïôûùüÿñæœ])', r'\1\2', text)
    return text, changes

# Function to handle the removal of unwanted spaces between paragraphs
def fix_paragraph_spaces(text):
    # Tokenize the text using SpaCy
    doc = nlp(text)
    
    # Initialize corrected text and change log
    corrected_text = []
    changes = []
    
    i = 0
    while i < len(doc):
        token = doc[i]
        if token.ent_type_ == 'PER' and i + 1 < len(doc) and doc[i + 1].is_alpha and doc[i + 1].is_lower:
            # Proper noun followed by lowercase word, ensure a space is added
            corrected_text.append(token.text + " ")
            changes.append(f"Ensured space after proper noun: {token.text}")
        else:
            corrected_text.append(token.text_with_ws)
        i += 1

    return "".join(corrected_text), changes

# Function to handle extra newlines between paragraphs
def remove_extra_newlines(text):
    # This regex looks for a line ending with a letter (uppercase or lowercase)
    # followed by one or more newlines, and then another letter (uppercase or lowercase)
    # at the beginning of the next line. It replaces the newlines with a single space.
    text = re.sub(r'([a-zA-ZàâçéèêëîïôûùüÿñæœÀÂÇÉÈÊËÎÏÔÛÙÜŸÆŒ])\n+\s*\n+\s*([a-zA-ZàâçéèêëîïôûùüÿñæœÀÂÇÉÈÊËÎÏÔÛÙÜŸÆŒ])', r'\1 \2', text)
    return text

# Function to handle spaces between sentences ending with lowercase and starting with lowercase
def merge_sentences(text):
    # Prevent merging if the next word starts with an uppercase letter
    text = re.sub(r'([a-zàâçéèêëîïôûùüÿñæœ,;])\s*\n\s*(?![A-Z])([a-zàâçéèêëîïôûùüÿñæœ])', r'\1 \2', text)
    return text

# Function to reduce space when a lowercase word ends a line and the next starts with a capital letter
def fix_line_breaks_between_sentences(text):
    # This regex looks for a lowercase word at the end of a line (no punctuation) 
    # followed by a line break and a capital letter at the beginning of the next line.
    text = re.sub(r'([a-zàâçéèêëîïôûùüÿñæœ])\s*\n\s*([A-Z])', r'\1 \2', text)
    return text

# New function to specifically correct common patterns and prevent incorrect merges
def fix_common_patterns(text):
    # Correct specific patterns like "peut-être", "Charlie pendant", "Liam se", etc.
    corrections = {
        r'peutêtre': 'peut-être',
        r'Charliependant': 'Charlie pendant',
        r'Alexiscontinue': 'Alexis continue',
        r'Liamse': 'Liam se'  # Specific case you've encountered
    }
    
    for pattern, replacement in corrections.items():
        text = re.sub(pattern, replacement, text)
    
    return text

def process_directory(input_dir, output_dir, logs_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    file_count = 0
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            log_path = os.path.join(logs_dir, f"{os.path.splitext(filename)[0]}_log.txt")

            with open(input_path, "r", encoding="utf-8") as file:
                text = file.read()

            # Add break times first
            text_with_breaks = add_break_times(text)

            # First scan to fix broken hyphens and merge lines
            corrected_text, changes = fix_broken_hyphens(text_with_breaks)
            # Second scan to ensure all cases are handled
            corrected_text, new_changes = fix_broken_hyphens(corrected_text)
            changes.extend(new_changes)
            # Third scan for any remaining cases
            corrected_text, more_changes = fix_broken_hyphens(corrected_text)
            changes.extend(more_changes)

            # Fix paragraph spaces and merge lines with proper nouns
            corrected_text, space_changes = fix_paragraph_spaces(corrected_text)
            changes.extend(space_changes)

            # Remove extra newlines between paragraphs
            corrected_text = remove_extra_newlines(corrected_text)

            # Fix line breaks between sentences where appropriate
            corrected_text = fix_line_breaks_between_sentences(corrected_text)

            # Merge sentences where needed, preventing improper merges
            final_text = merge_sentences(corrected_text)

            # Correct known problematic patterns
            final_text = fix_common_patterns(final_text)

            with open(output_path, "w", encoding="utf-8") as file:
                file.write(final_text)

            with open(log_path, "w", encoding="utf-8") as log:
                log.write(f"File: {filename}\n")
                for change in changes:
                    log.write(f"{change}\n")
                log.write("\n")

            file_count += 1
    
    if file_count == 0:
        logging.warning(f"No text files found in the input directory: {input_dir}")
    else:
        logging.info(f"Processed {file_count} files")

if __name__ == "__main__":
    input_dir = os.path.join("../", 'txt_processed/4-numbers_replaced')
    output_dir = os.path.join("../", 'txt_processed/5-line-fix')
    log_dir = os.path.join(output_dir, "logs")

    process_directory(input_dir, output_dir, logs_dir)
    logging.info("Script completed")
