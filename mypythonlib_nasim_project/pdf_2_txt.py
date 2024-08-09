#!/usr/bin/env python3
import os
import pdfplumber
import re
import sys

def clean_text(text, log_entries):
    # Define the generalized unwanted text pattern
    unwanted_pattern = re.compile(
        r'mmeepp.*\.iinndddd \d{1,5} \d{4}--\d{2}--\d{2} \d{2}::\d{2}'
    )
    
    # Find all unwanted patterns to log
    found_patterns = unwanted_pattern.findall(text)
    
    # Remove the unwanted text
    text = unwanted_pattern.sub('', text)
    
    # Additional cleaning to handle multiple consecutive spaces left after removal
    text = re.sub(r'\s{2,}', ' ', text)
    
    # Remove any leading or trailing whitespace
    text = text.strip()
    
    # Log the removed patterns
    for pattern in found_patterns:
        log_entries.append(f"Removed pattern: {pattern}")
    
    return text

def extract_text_with_filtering(page, log_entries):
    visible_text = []
    
    # Extract text lines
    lines = page.extract_text().splitlines()

    for line in lines:
        # Skip any lines that match the generalized unwanted pattern
        if re.search(r'mmeepp.*\.iinndddd', line):
            log_entries.append(f"Skipped line: {line}")
        else:
            visible_text.append(line)
    
    # Join the lines back into a single string with newlines
    return "\n".join(visible_text)

def extract_text_from_pdf(pdf_path, output_path, log_file_path):
    text = ""
    log_entries = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract visible text only
            page_text = extract_text_with_filtering(page, log_entries)
            if page_text:
                page_text = clean_text(page_text, log_entries)
                print(f"Extracted text from page {page_num}:\n{page_text}\n{'-'*40}\n")
                text += page_text + "\n\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    # Write log entries to the log file
    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write("\n".join(log_entries))

def process_directory(input_directory, output_directory, log_directory):
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(log_directory, exist_ok=True)

    for file_name in os.listdir(input_directory):
        if file_name.endswith('.pdf'):
            input_file_path = os.path.join(input_directory, file_name)
            output_file_name = f'{os.path.splitext(file_name)[0]}.txt'
            output_file_path = os.path.join(output_directory, output_file_name)
            log_file_name = f'log_{os.path.splitext(file_name)[0]}.txt'
            log_file_path = os.path.join(log_directory, log_file_name)

            print(f"Processing {file_name}...")
            extract_text_from_pdf(input_file_path, output_file_path, log_file_path)
            print(f"Processed file saved as {output_file_name}")

if __name__ == "__main__":
    input_directory = os.path.join("../", 'PDF_drop')
    output_directory = os.path.join("../", 'txt_processed/0-main_txt')
    log_directory = os.path.join(output_directory, 'logs')

    process_directory(input_directory, output_directory, log_directory)
    print("Script completed")
