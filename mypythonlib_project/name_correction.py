#!/usr/bin/env python3
import os
import re
import spacy
from config import output_directory  # Importing the output_directory from config.py

# Load SpaCy French large model
nlp = spacy.load('fr_core_news_lg')

# Function to extract and replace names
def extract_and_replace_names(text):
    doc = nlp(text)
    name_replacements = {
        'ez': 'ez', 'as': 'a', 'et': 'é', 'cer': 'cer', 'tier': 'tié', 'ault': 'o', 'ner': 'nèr',
        'ber': 'bèr', 'ars': 'ar', 'ère': 'èr', 'zier': 'zié', 'champ': 'chan', 'igny': 'ini',
        'nie': 'ni', 'ort': 'or', 'ard': 'ar', 'ières': 'ièr', 'aux': 'o', 'us': 'us',
        'ois': 'oi', 'is': 'i', 'ent': 'en', 'ert': 'èr', 'os': 'os', 'ot': 'o',
        'ah': 'a', 'ée': 'é', 'ès': 'è’sse', 'és': 'é', 'oix': 'oi', 'ets': 'et', 'ues': 'ue'
    }

    exception_names = [
        "Boris", "Paris", "Doris", "Elvis", "Curtis", "Travis", "Chris", "Dennis", "Francis", "Lewis", "Mars", "Julieet", 
        "Sébas", "Sergent", "Otis", "Phyllis", "Harris", "Morris", "Ennis", "Amaris", "Claris", "Wallis", "Jamis", "Yanis",
        # Add more exceptions as needed
    ]

    names = [ent.text for ent in doc.ents if ent.label_ == 'PER']
    unique_names = set(names)
    replaced_names = []
    log = {}

    for name in unique_names:
        if name in exception_names:
            continue  # Skip the replacement for exception names

        # Check if the word after the name starts with a capital letter
        next_token_index = doc.text.find(name) + len(name)
        if next_token_index < len(doc.text):
            next_token = doc.text[next_token_index:].split()[0]
            if next_token and not next_token[0].isupper():
                continue  # Skip if the next token is not capitalized

        for suffix, replacement in name_replacements.items():
            if name.endswith(suffix):
                new_name = name[:-len(suffix)] + replacement
                text = text.replace(name, new_name)
                replaced_names.append(new_name)
                log[name] = new_name
                break

    return text, log

# Function to clean text (preserving paragraph spacing)
def clean_text(text):
    # Preserve paragraph spacing by keeping double newlines
    text = re.sub(r'([.!?:])\s*\n\s*', r'\1\n\n', text)  # Ensure punctuation stays on the correct line and preserve spacing
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)  # Remove trailing spaces
    text = re.sub(r'[\t\x07]', '', text)  # Remove tabs and control characters
    return text

# Function to process text files and log replacements
def process_text_file(input_file_path, output_file_path, log_file_path, word_count):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Replace names and log them
    cleaned_text, replacements_log = extract_and_replace_names(text)

    # Clean up free spaces and control characters after a word
    cleaned_text = clean_text(cleaned_text)

    # Write the cleaned text to the output file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_text)

    # Log the name replacements - #bypass: To skip logging replacements, comment out this section
    #with open(log_file_path, 'w', encoding='utf-8') as log_file:
     #   for original, replacement in replacements_log.items():
      #      log_file.write(f"{original}: {replacement}\n")  # This logs each replacement

    # Count words and add to the total word count
    word_count += len(cleaned_text.split())
    return word_count

# Function to process text files in a directory and subdirectories
def process_directory(input_dir, output_dir, log_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Initialize total word count for each folder
    folder_word_count = {}

    # Walk through the input directory and subdirectories
    for root, dirs, files in os.walk(input_dir):
        # Exclude any folders that contain 'log', 'logs', etc. in their name
        dirs[:] = [d for d in dirs if 'log' not in d.lower()]

        # Process each .txt file in the current directory
        for file_name in files:
            if file_name.endswith('.txt'):
                input_file_path = os.path.join(root, file_name)

                # Determine output folder and log folder
                if root != input_dir:
                    relative_subfolder = os.path.relpath(root, input_dir)
                    output_subfolder = os.path.join(output_dir, relative_subfolder)

                    if not os.path.exists(output_subfolder):
                        os.makedirs(output_subfolder)

                    log_subfolder = os.path.join(output_subfolder, 'logs')
                    if not os.path.exists(log_subfolder):
                        os.makedirs(log_subfolder)

                    output_file_path = os.path.join(output_subfolder, file_name)
                    log_file_path = os.path.join(log_subfolder, f"log_{file_name}")
                    word_count_log_path = os.path.join(log_subfolder, "word_count.txt")
                else:
                    output_file_path = os.path.join(output_dir, file_name)
                    log_file_path = os.path.join(log_dir, f"log_{file_name}")
                    word_count_log_path = os.path.join(log_dir, "word_count.txt")

                # Initialize folder-specific word count if not present
                if word_count_log_path not in folder_word_count:
                    folder_word_count[word_count_log_path] = 0

                # Process the file and update folder-specific word count
                folder_word_count[word_count_log_path] += process_text_file(input_file_path, output_file_path, log_file_path, 0)

    # Log word count for each folder - #bypass: To skip logging word count, comment out this section
   # for word_count_log_path, total_word_count in folder_word_count.items():
    #    with open(word_count_log_path, 'w', encoding='utf-8') as wc_file:
     #       wc_file.write(f"Total word count for this folder: {total_word_count}\n")  # Logs total word count

if __name__ == "__main__":
    input_directory = os.path.join("../", "txt_processed/8-s_back_")
    log_directory = os.path.join(output_directory, 'logs_')

    process_directory(input_directory, output_directory, log_directory)
    print("Script completed")
