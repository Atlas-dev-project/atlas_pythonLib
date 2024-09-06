import fitz  # PyMuPDF
import os
import re

def extract_chapter_titles_pymupdf(pdf_path, log_file):
    try:
        doc = fitz.open(pdf_path)
        chapter_titles = []
        seen_titles = set()

        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"Processing PDF: {pdf_path}\n")
            log.flush()

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                blocks = page.get_text("dict")["blocks"]

                # Analyze each block to find potential chapter titles
                for block in blocks:
                    block_text = " ".join([span["text"] for line in block["lines"] for span in line["spans"]]).strip()
                    if not block_text:
                        continue

                    # Skip known non-chapter elements
                    if re.search(r'(catalogue|extrait|imprimerie|imprimé|reproduction)', block_text, re.IGNORECASE):
                        continue
                    
                    # Assume main font size is the most common one
                    font_sizes = [span["size"] for line in block["lines"] for span in line["spans"]]
                    if font_sizes:
                        main_font_size = max(set(font_sizes), key=font_sizes.count)

                    # Check if the block is at the top of the page, isolated, and has larger font size
                    block_is_isolated = block["bbox"][1] < 200 and len(block["lines"]) == 1
                    font_size = block["lines"][0]["spans"][0]["size"]

                    # Consider it a chapter title if the font size is significantly larger and it's isolated
                    if font_size > main_font_size * 1.5 and block_is_isolated and len(block_text.split()) < 10:
                        if block_text not in seen_titles:
                            chapter_titles.append(block_text)
                            seen_titles.add(block_text)

                            log.write(f"Extracted Chapter Title: {block_text}\n")
                            log.flush()
                            print(f"Extracted Chapter Title: {block_text}")

        return chapter_titles

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"Error processing {pdf_path}: {e}\n")
        return []

def save_titles_to_file(titles, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            formatted_titles = ",\n".join([f'"{title}"' for title in titles])
            f.write(formatted_titles)
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
            log_file_path = os.path.join(log_directory, f'{os.path.splitext(file_name)[0]}_log.txt')

            print(f"Processing {file_name}...")
            chapter_titles = extract_chapter_titles_pymupdf(input_file_path, log_file_path)
            save_titles_to_file(chapter_titles, output_file_path)
            print(f"Processed file saved as {output_file_name}")

if __name__ == "__main__":
    input_directory = os.path.join("../", 'PDF_drop')
    output_directory = os.path.join("../", 'txt_processed/11-chapter_titles')
    log_directory = os.path.join("../", 'logs')

    process_pdf_directory(input_directory, output_directory, log_directory)
    print("Script completed")
