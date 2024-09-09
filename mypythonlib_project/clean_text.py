#!/usr/bin/env python3
import os
import re
import sys

def clean_text(text):
    # Remove all occurrences of '@@'
    text = text.replace('@@', '')

    # Fix sentence spacing
    text = re.sub(r'(\S)\s*\n\s*(\S)', lambda m: f"{m.group(1)} {m.group(2)}" if m.group(1) != '.' and m.group(2).islower() else m.group(0), text)

    # Fix hyphenated words at line breaks
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)

    # Fix hyphenated words followed by a space
    text = re.sub(r'(\w)-\s+(\w)', r'\1-\2', text)

    # Remove spaces before and after hyphens
    text = re.sub(r'\s*-\s*', '-', text)

    # Remove leading and trailing spaces on each line
    text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)

    # Fix spaces around punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', text)

    # Remove spaces between em dashes and the following word
    text = re.sub(r'—\s+', '—', text)

    return text

def process_text_file(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Split text into paragraphs
    paragraphs = text.split('\n')

    cleaned_paragraphs = [clean_text(paragraph) for paragraph in paragraphs]

    cleaned_text = '\n'.join(cleaned_paragraphs)

    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_text)

# Modified function to process all text files in a directory and its subdirectories
def process_directory(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Walk through the directory and subdirectories
    for root, dirs, files in os.walk(input_directory):
        # Exclude any folders that contain 'log', 'logs', etc. in their name
        dirs[:] = [d for d in dirs if 'log' not in d.lower()]

        # Process files in the current directory
        for file_name in files:
            if file_name.endswith('.txt'):
                input_file_path = os.path.join(root, file_name)

                # Check if the file is in a subfolder
                if root != input_directory:
                    # Create corresponding subfolder in the output directory
                    relative_subfolder = os.path.relpath(root, input_directory)
                    output_subfolder = os.path.join(output_directory, relative_subfolder)

                    if not os.path.exists(output_subfolder):
                        os.makedirs(output_subfolder)

                    output_file_path = os.path.join(output_subfolder, file_name)
                else:
                    # Process files in the main input directory
                    output_file_path = os.path.join(output_directory, file_name)

                # Process the file as usual
                print(f"Processing {file_name} from {root}...")
                process_text_file(input_file_path, output_file_path)
                print(f"Processed file saved as {output_file_path}")

if __name__ == "__main__":
    input_directory = os.path.join("../", 'txt_processed/2-chapter_split')
    output_directory = os.path.join("../", 'txt_processed/3-paragraph_fix')

    process_directory(input_directory, output_directory)
    print("Script completed")
