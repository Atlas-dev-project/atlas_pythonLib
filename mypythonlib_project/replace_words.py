#!/usr/bin/env python3
import os
import json
import re

# Add the base directory to the PYTHONPATH
base_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the JSON file (one level up from mypythonlib_project)
json_file = os.path.join(os.path.dirname(base_dir), 'words_dictionary.json')

# Path to the txt_processed directory (two levels up from the current script)
txt_processed_dir = os.path.join(os.path.dirname(os.path.dirname(base_dir)), 'txt_processed')

# Directory paths within txt_processed
input_dir = os.path.join(txt_processed_dir, '6-5-es_ait_')
output_dir = os.path.join(txt_processed_dir, '7-word_replacement_')

# Print paths for debugging
print(f"Base Directory: {base_dir}")
print(f"JSON File Path: {json_file}")
print(f"Input Directory: {input_dir}")
print(f"Output Directory: {output_dir}")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

def flatten_nested_json(nested_json):
    flat_dict = {}
    for key, value in nested_json.items():
        if isinstance(value, dict):
            flat_dict.update(value)
        else:
            flat_dict[key] = value
    return flat_dict

def replace_words_using_json(json_file, input_dir, output_dir):
    # Load the content of the JSON file
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            nested_word_pairs = json.load(file)
    except FileNotFoundError:
        print(f"JSON file not found: {json_file}")
        return
    except json.JSONDecodeError:
        print(f"Error decoding JSON file: {json_file}")
        return

    # Flatten the nested JSON structure
    word_pairs = flatten_nested_json(nested_word_pairs)

    # Walk through the input directory and subdirectories
    for root, dirs, files in os.walk(input_dir):
        # Exclude any folders that contain 'log', 'logs', etc. in their name
        dirs[:] = [d for d in dirs if 'log' not in d.lower()]

        # Process each text file in the current directory
        for file_name in files:
            if file_name.endswith('.txt'):
                input_file_txt = os.path.join(root, file_name)
                print(f"\nProcessing file: {input_file_txt}\n")
                
                # Read the content of the text file
                with open(input_file_txt, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Track replaced words
                replaced_words = []

                # Replace words according to the pairs in the JSON file
                for word, replacement in word_pairs.items():
                    pattern = r'\b' + re.escape(word) + r'\b'
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        content, num_replacements = re.subn(pattern, replacement, content, flags=re.IGNORECASE)
                        replaced_words.append(f"{word} -> {replacement} (replaced {num_replacements} times)")
                        print(f"Replaced {word} with {replacement}: {num_replacements} times")

                # Determine output folder
                if root != input_dir:
                    # Create corresponding subfolder in the output directory
                    relative_subfolder = os.path.relpath(root, input_dir)
                    output_subfolder = os.path.join(output_dir, relative_subfolder)

                    if not os.path.exists(output_subfolder):
                        os.makedirs(output_subfolder)

                    # Create a 'logs' subfolder in the output subdirectory
                    log_subfolder = os.path.join(output_subfolder, 'logs')
                    if not os.path.exists(log_subfolder):
                        os.makedirs(log_subfolder)

                    output_file_txt = os.path.join(output_subfolder, file_name)
                    log_file_path = os.path.join(log_subfolder, f"{os.path.splitext(file_name)[0]}_log.txt")
                else:
                    output_file_txt = os.path.join(output_dir, file_name)
                    log_file_path = os.path.join(output_dir, 'logs', f"{os.path.splitext(file_name)[0]}_log.txt")

                # Ensure logs directory exists in the main output directory
                os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

                # Write the modified content to a new text file
                with open(output_file_txt, 'w', encoding='utf-8') as file:
                    file.write(content)

                # Write the summary of replaced words to a new log file
                with open(log_file_path, 'w', encoding='utf-8') as log_file:
                    log_file.write(f"Original file: {os.path.basename(input_file_txt)}\n\n")
                    log_file.write("Replaced words:\n")
                    if replaced_words:
                        log_file.write("\n".join(replaced_words) + "\n")
                    else:
                        log_file.write("No words were replaced.\n")

# Run the replacement function
replace_words_using_json(json_file, input_dir, output_dir)
