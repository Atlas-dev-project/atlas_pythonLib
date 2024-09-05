import os
import subprocess
import time
import logging
import sys

# Add the base directory to the PYTHONPATH
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(base_dir))  # Go two levels up
sys.path.append(base_dir)

# Define the path for the txt_processed directory two levels up
txt_processed_directory = os.path.join(parent_dir, "txt_processed")

# List of subdirectories relative to the txt_processed directory
subdirectories = [
    #"0-main_txt",
    "1-page_nb_cln",
    "2-chapter_split",
    "3-paragraph_fix",
    "4-numbers_replaced",
    "5-line-fix",
    "6-#@%_added_for_liasons",
    "6-5-es_ait_",
    "7-word_replacement_",
    "8-s_back_",
    "9-names_correction",
]

# List of Python scripts to run
script_paths = [
    #"pdf_2_txt.py",
    "remove_pnum_hilight_title.py",
    "split_chapters.py",
    "clean_text.py",
    "replace_numbers.py",
    "fix_lines.py",
    "liaisons.py",
    "ent_ait_fix.py",
    "replace_words.py",
    "replace_special_chars.py",
    "name_correction.py"
]

# Logging setup
log_file_path = os.path.join(base_dir, 'processing.log')

def setup_logging(log_file_path):
    logging.basicConfig(
        filename=log_file_path,
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        filemode='w'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

# Function to delete .txt files in the subdirectories
def delete_txt_files_in_subdirectories(base_directory, subdirectories):
    for subdir in subdirectories:
        full_path = os.path.join(base_directory, subdir)
        logging.debug(f"Deleting .txt files in: {full_path}")
        if os.path.exists(full_path):
            for root, dirs, files in os.walk(full_path):
                for file_name in files:
                    if file_name.endswith(".txt"):
                        file_path = os.path.join(root, file_name)
                        try:
                            os.remove(file_path)
                            logging.info(f"Deleted file: {file_path}")
                        except Exception as e:
                            logging.error(f"Error deleting file {file_path}: {e}")
        else:
            logging.warning(f"Directory does not exist: {full_path}")

# Function to update shebangs in scripts
def update_shebang(script_path):
    with open(script_path, 'r') as file:
        lines = file.readlines()

    if lines[0].startswith('#!'):
        lines[0] = f'#!/usr/bin/env python3\n'
    else:
        lines.insert(0, f'#!/usr/bin/env python3\n')

    with open(script_path, 'w') as file:
        file.writelines(lines)

def update_all_shebangs(script_paths):
    for script_path in script_paths:
        update_shebang(script_path)

# Function to run a script and log its output
def run_script(script_path):
    start_time = time.time()
    logging.debug(f"Running script: {script_path}")
    result = subprocess.run(['python3', script_path], capture_output=True, text=True)
    end_time = time.time()
    output = result.stdout.strip()
    errors = result.stderr.strip()

    logging.info(f"Finished running script: {script_path} in {end_time - start_time:.2f} seconds")
    logging.info(f"Output:\n{output}\n")
    if errors:
        logging.error(f"Errors:\n{errors}\n")

def ensure_directories_exist(base_directory, subdirectories):
    for subdir in subdirectories:
        dir_path = os.path.join(base_directory, subdir)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logging.info(f"Created directory: {dir_path}")

def main():
    start_time = time.time()
    script_paths_abs = [os.path.join(base_dir, script) for script in script_paths]

    # Set up logging
    setup_logging(log_file_path)

    # Ensure directories exist
    ensure_directories_exist(txt_processed_directory, subdirectories)

    # Delete .txt files in the specified subdirectories
    delete_txt_files_in_subdirectories(txt_processed_directory, subdirectories)

    # Update shebangs in all scripts
    update_all_shebangs(script_paths_abs)

    # Run scripts sequentially
    for script_path in script_paths_abs:
        run_script(script_path)

    total_time = time.time() - start_time
    logging.info(f"Total time for all tasks: {total_time:.2f} seconds")
    print(f"Total time for all tasks: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
