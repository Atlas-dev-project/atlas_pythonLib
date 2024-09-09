#!/usr/bin/env python3
import os
import spacy

# Directory paths
input_dir = os.path.join("../", 'txt_processed/6-#@%_added_for_liasons')
output_dir = os.path.join("../", 'txt_processed/6-5-es_ait_')
log_dir = os.path.join(output_dir, "logs")

# Load the SpaCy French large model
nlp = spacy.load("fr_core_news_lg")

# List of exception words
exception_words = ['laser', 'ressent', 'sister', 'insolent', 'content', 'vincent', 'absent', 'Laurent', 'Clement', 'Serpent', 'Advent', 'Ardent', 'baker', 'painter', 'runner', 'leader', 'writer', 'dancer', 'speaker', 'teacher']  # Add more words as needed

# Ensure output and log directories exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

def process_file(file_path, output_path, log_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    doc = nlp(text)

    es_replacements = 0
    er_replacements = 0
    ent_replacements = 0
    aient_replacements = 0

    es_replaced_words = []
    er_replaced_words = []
    ent_replaced_words = []
    aient_replaced_words = []

    new_text = []
    for i, token in enumerate(doc):
        if token.text.lower() in exception_words:
            new_text.append(token.text_with_ws)
            continue  # Skip further processing for exception words

        # Condition for "es" endings (Plural Nouns)
        if (token.tag_ == 'NOUN' and 'Number=Plur' in token.morph and token.text.endswith('es')
              and token.text.lower() != 'es'):
            next_token = doc[i + 1] if i < len(doc) - 1 else None
            if next_token and next_token.text[0].lower() not in 'aeiouà':
                new_word = token.text[:-1]
                new_text.append(new_word + token.whitespace_)
                es_replacements += 1
                es_replaced_words.append((token.text, new_word))
            else:
                new_text.append(token.text_with_ws)

        # Condition for "er" verbs (Infinitive to Past Participle)
        elif token.tag_ == 'VERB' and token.text.endswith('er'):
            new_word = token.text[:-2] + 'é'
            new_text.append(new_word + token.whitespace_)
            er_replacements += 1
            er_replaced_words.append((token.text, new_word))

        # Condition for "aient" endings (Third-person plural verbs)
        elif (token.tag_ == 'VERB' and 'Number=Plur' in token.morph and 'Person=3' in token.morph
              and token.text.endswith('aient')):
            new_word = token.text[:-3]  # Remove "aient" for third-person plural verbs
            new_text.append(new_word + token.whitespace_)
            aient_replacements += 1
            aient_replaced_words.append((token.text, new_word))

        # Fix: Only remove "nt" for third-person plural verbs ending in "ent"
        elif (token.tag_ == 'VERB' and 'Number=Plur' in token.morph and 'Person=3' in token.morph
              and token.text.endswith('ent')):
            new_word = token.text[:-2]  # Remove only "nt" from plural verbs
            new_text.append(new_word + token.whitespace_)
            ent_replacements += 1
            ent_replaced_words.append((token.text, new_word))

        else:
            new_text.append(token.text_with_ws)

    new_text = "".join(new_text)

    # Write the processed text to the output file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(new_text)

    # Write the log file
    with open(log_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"File: {file_path}\n")
        log_file.write(f"Total 'es' replacements: {es_replacements}\n")
        log_file.write("Replacements made for 'es':\n")
        for original, new in es_replaced_words:
            log_file.write(f"Replaced '{original}' with '{new}'\n")

        log_file.write(f"\nTotal 'er' replacements: {er_replacements}\n")
        log_file.write("Replacements made for 'er':\n")
        for original, new in er_replaced_words:
            log_file.write(f"Replaced '{original}' with '{new}'\n")

        log_file.write(f"\nTotal 'aient' replacements: {aient_replacements}\n")
        log_file.write("Replacements made for 'aient':\n")
        for original, new in aient_replaced_words:
            log_file.write(f"Replaced '{original}' with '{new}'\n")

        log_file.write(f"\nTotal 'ent' replacements: {ent_replacements}\n")
        log_file.write("Replacements made for 'ent':\n")
        for original, new in ent_replaced_words:
            log_file.write(f"Replaced '{original}' with '{new}'\n")

# Modified function to process text files in a directory and subdirectories
def process_directory(input_dir, output_dir, log_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Walk through the directory and subdirectories
    for root, dirs, files in os.walk(input_dir):
        # Exclude any folders that contain 'log', 'logs', etc. in their name
        dirs[:] = [d for d in dirs if 'log' not in d.lower()]

        # Process files in the current directory
        for filename in files:
            if filename.endswith('.txt'):
                input_path = os.path.join(root, filename)

                # Check if the file is in a subfolder
                if root != input_dir:
                    # Create corresponding subfolder in the output directory
                    relative_subfolder = os.path.relpath(root, input_dir)
                    output_subfolder = os.path.join(output_dir, relative_subfolder)
                    log_subfolder = os.path.join(output_subfolder, 'logs')

                    if not os.path.exists(output_subfolder):
                        os.makedirs(output_subfolder)

                    if not os.path.exists(log_subfolder):
                        os.makedirs(log_subfolder)

                    output_path = os.path.join(output_subfolder, filename)
                    log_path = os.path.join(log_subfolder, f"{os.path.splitext(filename)[0]}_log.txt")
                else:
                    # Process files in the main input directory
                    output_path = os.path.join(output_dir, filename)
                    log_path = os.path.join(log_dir, f"{os.path.splitext(filename)[0]}_log.txt")

                process_file(input_path, output_path, log_path)

if __name__ == "__main__":
    process_directory(input_dir, output_dir, log_dir)
    print("Processing complete.")
