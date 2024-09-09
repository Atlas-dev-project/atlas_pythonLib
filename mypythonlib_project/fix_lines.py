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

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Function to check if a word is valid using SpaCy
def is_valid_word(word):
    doc = nlp(word)
    return len(doc) == 1 and doc[0].is_alpha

# Function to remove hyphens that break words at the end of lines and log the changes
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
                # Ensure next line does not start with capital letter or the word is not a proper noun
                if is_valid_word(combined_word) and after.islower() and not next_line[0].isupper():
                    changes.append(f"Removed hyphen in: {last_word} -> {combined_word}")
                    # Remove the hyphen and merge the lines correctly
                    line = line[:-len(last_word)] + combined_word + next_line[len(after):].lstrip()
                    i += 1  # Skip next line as it has been merged
        corrected_text.append(line)
        i += 1

    # Ensure proper merging of broken words without adding extra spaces
    text = re.sub(r'([a-zàâçéèêëîïôûùüÿñæœ,;])-\s*\n\s*(?![A-Z])([a-zàâçéèêëîïôûùüÿñæœ])', r'\1\2', "\n".join(corrected_text))
    return text, changes

# Function to handle the removal of unwanted spaces between paragraphs using SpaCy
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

# Function to remove extra newlines between paragraphs
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

# Function to correct common patterns like "peut-être"
def fix_common_patterns(text):
    corrections = {
        r'peutêtre': 'peut-être',
        r'Charliependant': 'Charlie pendant',
        r'Alexiscontinue': 'Alexis continue',
        r'Liamse': 'Liam se'
    }
    
    for pattern, replacement in corrections.items():
        text = re.sub(pattern, replacement, text)
    
    return text


# Function to ensure natural paragraph breaks by adding a paragraph break when a new line starts without a double newline
def ensure_natural_paragraph_breaks(text):
    # Look for periods followed by a single newline and some text, insert an extra newline
    text = re.sub(r'(\.\s*)\n(?!\n)', r'\1\n\n', text)
    return text

# Function to ensure exactly one space after dashes/hyphens
def fix_spaces_after_dashes(text):
    # This regex looks for lines that start with "–" followed by either no space or multiple spaces,
    # and ensures exactly one space remains.
    text = re.sub(r'^(–)\s*', r'\1 ', text, flags=re.MULTILINE)
    return text


# New function to reduce multiple empty lines to one
def reduce_multiple_empty_lines(text):
    # Replace multiple newlines with just one
    return re.sub(r'\n{3,}', r'\n\n', text)

# Second step: Add paragraph breaks after 4 lines of text, after the nearest period, ensuring no orphan phrases
def add_paragraph_breaks(text):
    lines = text.splitlines()  # Split the text into lines
    new_lines = []  # List to hold the processed lines
    consecutive_line_count = 0  # Track the number of consecutive non-empty lines
    buffer = []  # Temporary buffer to hold lines before committing them to new_lines

    for i, line in enumerate(lines):
        buffer.append(line)  # Add the current line to the buffer
        if line.strip():  # If the line is not empty, increment the count
            consecutive_line_count += 1
        else:
            consecutive_line_count = 0  # Reset count on empty lines

        # Add paragraph space after 4 consecutive lines of text at the nearest period
        if consecutive_line_count == 4:
            period_index = line.rfind('.')  # Find the last period in the line
            if period_index != -1 and not re.match(r'[.]{2,}', line[period_index+1:]):  # Avoid adding space after ellipses (...)
                # Check if the next line starts with a hyphen or dash, don't add a paragraph break if so
                if i + 1 < len(lines) and lines[i + 1].lstrip().startswith('—'):
                    continue  # Skip adding a paragraph break

                # Check if the period is followed by any symbol like » or )
                post_period_text = line[period_index+1:].strip()
                if post_period_text and post_period_text[0] in ['»', ')']:
                    buffer[-1] = line[:period_index+1] + post_period_text[0]  # Include the symbol with the period
                    buffer.append("")  # Add paragraph break after the symbol
                    buffer.append(post_period_text[1:].strip())  # Add the rest of the line after the symbol
                else:
                    buffer[-1] = line[:period_index+1]  # Keep everything up to the period
                    buffer.append("")  # Add paragraph break
                    buffer.append(line[period_index+1:].strip())  # Add the text after the period
                
                consecutive_line_count = 0  # Reset the count after inserting a paragraph break
                
                # Avoid leaving a single line alone by checking the buffer
                if len(buffer) > 1 and buffer[-2] == "":  # If the last paragraph has only one line
                    # Move the last line up to avoid the orphan phrase
                    last_line = buffer.pop()
                    buffer[-1] = buffer[-1] + " " + last_line  # Combine the orphan with the previous line
            consecutive_line_count = 0

        new_lines.extend(buffer)  # Commit buffer lines to new_lines
        buffer = []  # Clear the buffer for the next set of lines

    return "\n".join(new_lines)  # Join the processed lines back into a single string


# Function to process files in the directory with three scans for hyphen fixes
def process_directory(input_dir, output_dir):
    file_count = 0
    for root, dirs, files in os.walk(input_dir):
        dirs[:] = [d for d in dirs if 'log' not in d.lower()]  # Exclude 'log' directories

        for filename in files:
            if filename.endswith(".txt"):
                input_path = os.path.join(root, filename)
                relative_subfolder = os.path.relpath(root, input_dir)
                output_subfolder = os.path.join(output_dir, relative_subfolder)
                log_subfolder = os.path.join(output_subfolder, 'logs')

                if not os.path.exists(output_subfolder):
                    os.makedirs(output_subfolder)

                if not os.path.exists(log_subfolder):
                    os.makedirs(log_subfolder)

                output_path = os.path.join(output_subfolder, filename)
                log_path = os.path.join(log_subfolder, f"{os.path.splitext(filename)[0]}_log.txt")

                with open(input_path, "r", encoding="utf-8") as file:
                    text = file.read()

                changes = []

                # First scan to fix broken hyphens
                corrected_text, hyphen_changes = fix_broken_hyphens(text)
                changes.extend(hyphen_changes)

                # Second scan to ensure all cases are handled
                corrected_text, new_changes = fix_broken_hyphens(corrected_text)
                changes.extend(new_changes)

                # Third scan for any remaining cases
                corrected_text, more_changes = fix_broken_hyphens(corrected_text)
                changes.extend(more_changes)

                # Fix paragraph spaces
                corrected_text, space_changes = fix_paragraph_spaces(corrected_text)
                changes.extend(space_changes)

                # Remove extra newlines
                corrected_text = remove_extra_newlines(corrected_text)

                # Fix line breaks between sentences
                corrected_text = fix_line_breaks_between_sentences(corrected_text)

                # Merge sentences
                corrected_text = merge_sentences(corrected_text)

                # Ensure natural paragraph breaks
                corrected_text = ensure_natural_paragraph_breaks(corrected_text)

                # Add paragraph breaks after 4 lines
                corrected_text = add_paragraph_breaks(corrected_text)

                # Reduce multiple empty lines to just one
                final_text = reduce_multiple_empty_lines(corrected_text)

                # Reduce spaces after dashes
                final_text = fix_spaces_after_dashes(final_text)

                # Correct known problematic patterns
                final_text = fix_common_patterns(final_text)

                with open(output_path, "w", encoding="utf-8") as file:
                    file.write(final_text)

                with open(log_path, "w", encoding="utf-8") as log_file:
                    log_file.write(f"File: {filename}\n")
                    for change in changes:
                        log_file.write(f"{change}\n")
                    log_file.write("\n")

                file_count += 1
    
    if file_count == 0:
        logging.warning(f"No text files found in the input directory: {input_dir}")
    else:
        logging.info(f"Processed {file_count} files")

if __name__ == "__main__":
    input_dir = os.path.join("../", 'txt_processed/4-numbers_replaced')
    output_dir = os.path.join("../", 'txt_processed/5-line-fix')

    process_directory(input_dir, output_dir)
    logging.info("Script completed")
