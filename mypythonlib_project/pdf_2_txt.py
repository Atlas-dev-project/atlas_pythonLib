#!/usr/bin/env python3
import fitz  # PyMuPDF
import os
import re
from collections import defaultdict

def extract_text_with_formatting(pdf_path, log_file):
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        removal_count = defaultdict(int)  # Dictionary to count removed items (like page numbers)

        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"Processing PDF: {pdf_path}\n")
            log.flush()

            previous_line = ""  # To track the previous line for joining

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                blocks = page.get_text("blocks")
                blocks = sorted(blocks, key=lambda b: (b[1], b[0]))  # Sort blocks by vertical position

                for block in blocks:
                    block_text = block[4].strip().splitlines()

                    for i, line in enumerate(block_text):
                        line = line.strip()

                        # Check if the line is just a page number and remove it
                        if re.match(r'^\d+$', line):
                            removal_count["Page Number"] += 1
                            log.write(f"Removed: {line} (Page Number)\n")
                            log.flush()
                            continue

                        # Handle apostrophe case ("L'" or "l'")
                        if previous_line.endswith("L") and line.startswith("’"):
                            previous_line += line  # Join "L" and "’" into "L'"
                            log.write(f"Joined L': {previous_line}\n")
                            continue

                        # Join lines where the previous line ends without punctuation and the current line starts with punctuation
                        if previous_line and not previous_line.endswith(('.', '!', '?', ':')) and line.startswith(('?', ':', '!', '»', '«')):
                            previous_line += line  # Join previous line and current punctuation
                            log.write(f"Joined punctuation line: {previous_line}\n")
                            continue

                        # Add the previous line to the full text
                        if previous_line:
                            full_text += previous_line + "\n"

                        # Update the previous line to the current line
                        previous_line = line

                # Add any remaining line to the full text
                if previous_line:
                    full_text += previous_line + "\n"
                    previous_line = ""  # Clear the previous line after adding it

                full_text += "\n"  # Add spacing between pages

            # Write a summary of removed items at the end of the log
            log.write(f"\nSummary of removed items for PDF: {pdf_path}\n")
            log.write(f"{'Item':<50} {'Count':<10}\n")
            log.write("="*60 + "\n")
            for item, count in removal_count.items():
                log.write(f"{item:<50} {count:<10}\n")

        return full_text

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"Error processing {pdf_path}: {e}\n")
        return ""

def save_text_to_file(text, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception as e:
        print(f"Error saving file {output_path}: {e}")

def process_pdf_directory(input_directory, output_directory, log_directory):
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(log_directory, exist_ok=True)

    for file_name in os.listdir(input_directory):
        if file_name.endswith('.pdf'):
            input_file_path = os.path.join(input_directory, file_name)
            output_file_name = f'{os.path.splitext(file_name)[0]}.txt'
            output_file_path = os.path.join(output_directory, output_file_name)

            # Log file path with the same name as the PDF but with a "_log.txt" suffix
            log_file_path = os.path.join(log_directory, f'{os.path.splitext(file_name)[0]}_log.txt')

            print(f"Processing {file_name}...")
            extracted_text = extract_text_with_formatting(input_file_path, log_file_path)
            save_text_to_file(extracted_text, output_file_path)
            print(f"Processed file saved as {output_file_name}")

if __name__ == "__main__":
    input_directory = os.path.join("../", 'PDF_drop')
    output_directory = os.path.join("../", 'txt_processed/0-main_txt')
    log_directory = os.path.join(output_directory, 'logs')

    process_pdf_directory(input_directory, output_directory, log_directory)
    print("Script completed")
