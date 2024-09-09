#!/usr/bin/env python3
import os
import shutil
import sys
from config import input_directory  # Import only the input_directory from config.py

# Function to copy subfolders from input to output directory
def copy_subfolders(input_dir, output_dir):
    for item in os.listdir(input_dir):
        subdir_path = os.path.join(input_dir, item)
        if os.path.isdir(subdir_path):
            dest_dir = os.path.join(output_dir, item)
            try:
                shutil.copytree(subdir_path, dest_dir)
                print(f"Copied folder: {subdir_path} to {dest_dir}")
            except Exception as e:
                print(f"Error copying folder {subdir_path}: {e}")

def main():
    # Output directory remains defined directly in the script
    output_directory = os.path.join("../", "txt_processed/0-main_txt")

    # Copy subfolders using input_directory from config.py
    copy_subfolders(input_directory, output_directory)

if __name__ == "__main__":
    main()
