#!/usr/bin/env python3
import os
import re

def split_into_chapters(text):
    # Split the text by chapter markers, retaining the markers
    chapter_splits = re.split(r'(@@.*?@@)', text, flags=re.DOTALL)
    chapters = []

    # Iterate over the chapter splits and merge titles with their content
    for i in range(1, len(chapter_splits), 2):
        chapter_title = chapter_splits[i].strip()
        chapter_content = chapter_splits[i + 1].strip() if (i + 1) < len(chapter_splits) else ''
        formatted_chapter = f"{chapter_title}\n\n{chapter_content}"
        chapters.append(formatted_chapter)

    return chapters

def process_text_file(input_file_path, output_subfolder, info_output_subfolder):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # If no @@ markers are found, export the full text to the next folder
    if '@@' not in text:
        output_file_path = os.path.join(output_subfolder, os.path.basename(input_file_path))
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(text.strip())
        print(f"No chapter markers found. Full text exported to: {output_file_path}")
        return

    # Extract and save book info before the first @@ marker
    book_info = text.split('@@', 1)[0].strip()
    info_file_path = os.path.join(info_output_subfolder, os.path.basename(input_file_path).replace('.txt', '_info.txt'))
    with open(info_file_path, 'w', encoding='utf-8') as info_file:
        info_file.write(book_info)
    print(f"Book info saved to: {info_file_path}")

    # Start processing from the first @@ marker
    text = text.split('@@', 1)[1]
    text = '@@' + text  # Add the marker back to the beginning

    chapters = split_into_chapters(text)

    for index, chapter in enumerate(chapters):
        output_file_name = f"Chapitre_{index + 1}.txt"
        output_file_path = os.path.join(output_subfolder, output_file_name)

        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(chapter.strip())
        print(f"Processed file saved to: {output_file_path}")

# Function to process all text files in a directory and its subdirectories
def process_directory(input_directory, output_directory, info_output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    if not os.path.exists(info_output_directory):
        os.makedirs(info_output_directory)

    # Walk through the directory and subdirectories
    for root, dirs, files in os.walk(input_directory):
        # Exclude any folders that contain 'log', 'logs', etc. in their name
        dirs[:] = [d for d in dirs if 'log' not in d.lower()]

        # Process files in the current directory
        for file_name in sorted(files):  # Sort files to process them in order
            if file_name.endswith('.txt'):
                input_file_path = os.path.join(root, file_name)

                # If the file is in a subfolder of the input directory, create the corresponding subfolder in the output
                if root != input_directory:
                    # Create a subfolder in the output directory named after the original subfolder
                    relative_subfolder = os.path.relpath(root, input_directory)
                    output_subfolder = os.path.join(output_directory, relative_subfolder)
                    info_output_subfolder = os.path.join(info_output_directory, relative_subfolder)

                    if not os.path.exists(output_subfolder):
                        os.makedirs(output_subfolder)
                    if not os.path.exists(info_output_subfolder):
                        os.makedirs(info_output_subfolder)

                else:
                    # If the file is in the root input directory, save directly to the output directory
                    output_subfolder = output_directory
                    info_output_subfolder = info_output_directory

                # Process the file as usual
                print(f"Processing {file_name} from {root}...")
                process_text_file(input_file_path, output_subfolder, info_output_subfolder)
                print(f"Processed file saved to {output_subfolder}")

if __name__ == "__main__":
    input_directory = os.path.join("../", 'txt_processed/1-page_nb_cln')
    output_directory = os.path.join("../", 'txt_processed/2-chapter_split')
    info_output_directory = os.path.join("../", 'txt_processed/10-book_info')

    process_directory(input_directory, output_directory, info_output_directory)
    print("Script completed")
