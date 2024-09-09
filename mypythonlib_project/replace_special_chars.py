#!/usr/bin/env python3
import os
import re

# Directory paths
input_dir = os.path.join("../", "txt_processed/7-word_replacement_")
output_dir = os.path.join("../", "txt_processed/8-s_back_")
log_dir = os.path.join(output_dir, "logs")

# Ensure the output directories exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# Function to process each file and replace occurrences
def process_file(file_path, output_file_path, log_file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find and replace all occurrences of #@%
    replacements = {
        r'#@%': 's'
    }
    
    replaced_words = []
    
    for pattern, replacement in replacements.items():
        occurrences = re.findall(pattern, content)
        if occurrences:
            replaced_words.extend([(occurrence, replacement) for occurrence in occurrences])
            content = re.sub(pattern, replacement, content)
    
    # Write the processed content to a new file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    # Log the replacements
    if replaced_words:
        with open(log_file_path, 'w', encoding='utf-8') as log_file:
            log_file.write(f"File: {os.path.basename(file_path)}\n")
            for old, new in replaced_words:
                log_file.write(f"Replaced: {old} with '{new}'\n")
            log_file.write("\n")

# Modified function to process text files in a directory and subdirectories
def process_directory(input_dir, output_dir, log_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Walk through the input directory and subdirectories
    for root, dirs, files in os.walk(input_dir):
        # Exclude any folders that contain 'log', 'logs', etc. in their name
        dirs[:] = [d for d in dirs if 'log' not in d.lower()]

        # Process each .txt file in the current directory
        for filename in files:
            if filename.endswith(".txt") and not filename.endswith("_processed.txt"):
                input_file_path = os.path.join(root, filename)

                # Determine output folder and log folder
                if root != input_dir:
                    # Create corresponding subfolder in the output directory
                    relative_subfolder = os.path.relpath(root, input_dir)
                    output_subfolder = os.path.join(output_dir, relative_subfolder)

                    if not os.path.exists(output_subfolder):
                        os.makedirs(output_subfolder)

                    # Create a separate log folder inside the output subfolder
                    log_subfolder = os.path.join(output_subfolder, 'logs')
                    if not os.path.exists(log_subfolder):
                        os.makedirs(log_subfolder)

                    output_file_path = os.path.join(output_subfolder, filename.replace(".txt", "_processed.txt"))
                    log_file_path = os.path.join(log_subfolder, f"{os.path.splitext(filename)[0]}_log.txt")
                else:
                    output_file_path = os.path.join(output_dir, filename.replace(".txt", "_processed.txt"))
                    log_file_path = os.path.join(log_dir, f"{os.path.splitext(filename)[0]}_log.txt")

                # Process the file
                process_file(input_file_path, output_file_path, log_file_path)

if __name__ == "__main__":
    process_directory(input_dir, output_dir, log_dir)
    print("Processing complete.")
