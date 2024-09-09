#!/usr/bin/env python3
import os
import re
from num2words import num2words

# Function to handle some preprocessing before number replacement
def process_text_before_replacement(text):
    log_entries = []
    
    # Replace 'h' or 'hr' with 'heure' when preceded by a number
    text = re.sub(r'(\d+)[\s]*?(h|hr)', lambda match: f"{match.group(1)} heure", text)
    log_entries.append("Replaced 'h' or 'hr' with 'heure' when preceded by a number")
    
    # Replace cases like "1.1", "1. 1", "1 . 1" with "1 point 1," (with a comma at the end)
    text = re.sub(r'(\b\d+\b)\s*\.\s*(\b\d+\b)', replace_decimal_with_words, text)
    log_entries.append("Replaced decimal notation with 'point' and added a comma")

    return text, log_entries

# Function to replace decimals with "point" in words (e.g., "1.1" or "1 . 1" becomes "un point un,")
def replace_decimal_with_words(match):
    number_part1 = int(match.group(1))
    number_part2 = int(match.group(2))
    
    words_part1 = num2words(number_part1, lang='fr')
    words_part2 = num2words(number_part2, lang='fr')
    
    result = f"{words_part1} point {words_part2},"
    return result

# Function to replace numbers with words
def replace_numbers_with_words(text):
    log_entries = []
    text, additional_log_entries = process_text_before_replacement(text)
    log_entries.extend(additional_log_entries)

    # Function to replace individual numbers
    def replace_number(match):
        number = int(match.group())
        words = num2words(number, lang='fr')
        log_entries.append(f"{number}: {words}")
        return words

    # Replace numbers in the text
    text = re.sub(r'\b([0-9]{1,6})\b', replace_number, text)
    
    return text, log_entries

# Function to add break tags to the text
def add_break_tags(text):
    # Add <break time="0.8s" /> at the beginning
    text = f'<break time="0.8s" />\n{text}'
    
    # Add <break time="2.8s" /> at the end
    text = f'{text}\n<break time="2.8s" />'
    
    # Add <break time="2.0s" /> after the first empty paragraph space
    text = re.sub(r'(\n\s*\n)', r'\1<break time="2.0s" />\n', text, count=1)

    return text

# Function to process a single text file
def process_text_file(input_file_path, output_file_path, log_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Replace numbers with words and add break tags
    cleaned_text, log_entries = replace_numbers_with_words(text)

    # Add break tags at the required places
    cleaned_text = add_break_tags(cleaned_text)

    # Write the processed text file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_text)

    # Write the log file
    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write("\n".join(log_entries))

# Function to process all text files in a directory and its subdirectories
def process_directory(input_directory, output_directory, log_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Walk through the directory and subdirectories
    for root, dirs, files in os.walk(input_directory):
        # Exclude any folders that contain 'log', 'logs', etc. in their name
        dirs[:] = [d for d in dirs if 'log' not in d.lower()]

        # Process files in the current directory
        for file_name in files:
            if file_name.endswith('.txt') and 'log' not in file_name.lower():
                input_file_path = os.path.join(root, file_name)

                # Check if the file is in a subfolder
                if root != input_directory:
                    # Create corresponding subfolder in the output directory
                    relative_subfolder = os.path.relpath(root, input_directory)
                    output_subfolder = os.path.join(output_directory, relative_subfolder)

                    if not os.path.exists(output_subfolder):
                        os.makedirs(output_subfolder)

                    output_file_path = os.path.join(output_subfolder, file_name)
                    log_subdirectory = os.path.join(output_subfolder, 'logs')
                    if not os.path.exists(log_subdirectory):
                        os.makedirs(log_subdirectory)
                    log_file_path = os.path.join(log_subdirectory, f'log_{os.path.splitext(file_name)[0]}.txt')
                else:
                    # Process files in the main input directory
                    output_file_path = os.path.join(output_directory, file_name)
                    log_file_path = os.path.join(log_directory, f'log_{os.path.splitext(file_name)[0]}.txt')

                # Process the file as usual
                print(f"Processing {file_name} from {root}...")
                process_text_file(input_file_path, output_file_path, log_file_path)
                print(f"Processed file saved as {output_file_path}")

if __name__ == "__main__":
    input_directory = os.path.join("../", "txt_processed/3-paragraph_fix")
    output_directory = os.path.join("../", "txt_processed/4-numbers_replaced")
    log_directory = os.path.join(output_directory, "logs")

    process_directory(input_directory, output_directory, log_directory)
    print("Script completed")
