#!/usr/bin/env python3
import fitz  # PyMuPDF
import os
import re
from collections import defaultdict

# Function to extract text with formatting and remove annotation numbers
def extract_text_with_formatting(pdf_path, log_file, annotation_file):
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        removal_count = defaultdict(int)  # Dictionary to count removed items (like page numbers)
        annotation_numbers = []  # To store annotation numbers removed
        removed_annotations = set()  # Set to track removed annotation numbers
        annotations_extracted = False  # Flag to track if any annotations were extracted
        annotation_paragraphs = []  # Store annotation and associated paragraph

        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"Processing PDF: {pdf_path}\n")
            log.flush()

            previous_line = ""  # Track the previous line for joining
            annotation_pattern = re.compile(r'([a-zA-ZéèêëîïôœùûüçÉÈÊËÎÏÔŒÙÛÜÇ]+)(\d{1,3})')  # Capture annotations like word16

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                blocks = page.get_text("blocks")
                blocks = sorted(blocks, key=lambda b: (b[1], b[0]))  # Sort blocks by vertical position

                for block in blocks:
                    block_text = block[4].strip().splitlines()

                    for i, line in enumerate(block_text):
                        line = line.strip()

                        # Check for annotation numbers attached to words (like word16)
                        annotation_match = annotation_pattern.search(line)
                        if annotation_match:
                            preceding_word = annotation_match.group(1)
                            annotation_number = annotation_match.group(2)

                            # Only remove the annotation if it hasn't been removed already
                            if annotation_number not in removed_annotations:
                                line = annotation_pattern.sub(lambda m: f"{m.group(1)}", line)  # Remove the number but keep the word
                                annotation_numbers.append(f"{preceding_word} {annotation_number}")
                                removal_count["Annotation Number"] += 2
                                removed_annotations.add(annotation_number)  # Mark this annotation as removed
                                annotations_extracted = True  # Mark that an annotation was extracted
                                log.write(f"Removed annotation number: {annotation_number} (Attached to word: {preceding_word})\n")
                                log.flush()

                                # Check if the annotation number exists in the following paragraph (footnote/endnote)
                                for j in range(i + 1, len(block_text)):
                                    next_line = block_text[j].strip()
                                    if next_line.startswith(annotation_number):
                                        annotation_paragraphs.append(f"{annotation_number}: {next_line}")
                                        log.write(f"Extracted annotation: {annotation_number} -> {next_line}\n")
                                        break

                        # Check if the line is just a standalone page number and remove it
                        if re.match(r'^\d+$', line):
                            if (i == 0 or not block_text[i - 1].strip()) and (i == len(block_text) - 1 or not block_text[i + 1].strip()):
                                removal_count["Page Number"] += 1
                                log.write(f"Removed: {line} (Standalone Page Number)\n")
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

            # Write annotation numbers and their extracted paragraphs to a separate file if any were found
            if annotations_extracted:
                with open(annotation_file, 'w', encoding='utf-8') as af:
                    af.write("Annotations Extracted:\n")
                    for annotation in annotation_numbers:
                        af.write(f"{annotation}\n")
                    af.write("\nExtracted Annotation Paragraphs:\n")
                    for annotation_para in annotation_paragraphs:
                        af.write(f"{annotation_para}\n")
            else:
                # If no annotations, write to log
                log.write("No annotations extracted or removed.\n")

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

# Function to save extracted text to a file
def save_text_to_file(text, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception as e:
        print(f"Error saving file {output_path}: {e}")

# Function to process a directory of PDFs
def process_pdf_directory(input_directory, output_directory):
    for root, dirs, files in os.walk(input_directory):
        for file_name in files:
            if file_name.endswith('.pdf'):
                input_file_path = os.path.join(root, file_name)

                # Determine the output folder
                if root != input_directory:
                    relative_subfolder = os.path.relpath(root, input_directory)
                    output_subfolder = os.path.join(output_directory, relative_subfolder)
                else:
                    output_subfolder = os.path.join(output_directory, os.path.splitext(file_name)[0])

                os.makedirs(output_subfolder, exist_ok=True)

                output_file_name = f'{os.path.splitext(file_name)[0]}.txt'
                output_file_path = os.path.join(output_subfolder, output_file_name)

                log_subfolder = os.path.join(output_subfolder, 'logs')
                os.makedirs(log_subfolder, exist_ok=True)

                log_file_path = os.path.join(log_subfolder, f'{os.path.splitext(file_name)[0]}_log.txt')
                annotation_file_path = os.path.join(log_subfolder, 'annotation_extracted.txt')

                print(f"Processing {file_name}...")
                extracted_text = extract_text_with_formatting(input_file_path, log_file_path, annotation_file_path)
                save_text_to_file(extracted_text, output_file_path)
                print(f"Processed file saved as {output_file_name} in {output_subfolder}")

if __name__ == "__main__":
    input_directory = os.path.join("../", 'PDF_drop')
    output_directory = os.path.join("../", 'txt_processed/0-main_txt')

    process_pdf_directory(input_directory, output_directory)
    print("Script completed")
