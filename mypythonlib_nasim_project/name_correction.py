#!/usr/bin/env python3
import os
import re
import spacy
from ebooklib import epub  # For creating EPUB files

# Load SpaCy French large model
nlp = spacy.load('fr_core_news_lg')

# Function to extract and replace names
def extract_and_replace_names(text):
    doc = nlp(text)
    name_replacements = {
        'ez': 'ez', 'as': 'a', 'et': 'é', 'cer': 'cer', 'tier': 'tié', 'ault': 'o', 'ner': 'nèr',
        'ber': 'bèr', 'ars': 'ar', 'ère': 'èr', 'zier': 'zié', 'champ': 'chan', 'igny': 'ini',
        'nie': 'ni', 'ort': 'or', 'ard': 'ar', 'ières': 'ièr', 'aux': 'o', 'us': 'us',
        'ois': 'oi', 'is': 'i', 'ent': 'en', 'ert': 'èr', 'os': 'os', 'ot': 'o',
        'ah': 'a', 'ée': 'é', 'ès': 'è’sse', 'és': 'é', 'oix': 'oi', 'ets': 'et', 'ues': 'ue'
    }

    exception_names = [
        "Boris", "Paris", "Doris", "Elvis", "Curtis", "Travis", "Chris", "Dennis", "Francis", "Lewis", "Mars", "Julieet", 
        "Sébas", "Sergent", "Otis", "Phyllis", "Harris", "Morris", "Ennis", "Amaris", "Claris", "Wallis", "Jamis", "Yanis",
        "Loris", "Ellis", "Anis", "Idris", "Euris", "Mavis", "Norris", "Tavis", "Maris", "Candis", "Jadis", "Farris", 
        "Ferris", "Avis", "Alis", "Eddis", "Iris", "Janis", "Jarvis", "Karis", "Ladis", "Vas-y fort", "Genesis", "Nelis", 
        "Bris", "Chrys", "Daris", "Elis", "Eris", "Hollis", "Kelis", "Thais", "Nokomis", "Vallis", "Aulis", "Aris", 
        "Clematis", "Clovis", "Damaris", "Ignis", "Rufus", "Silas", "Vas", "Windigos", "Assis", "Achilles", "Cris", 
        "Iris", "Myrtis", "Narcis", "Peris", "Tallis", "Yanis", "Siris", "Annis", "Chris", "Davis", "Bigfoot", "Bigfoots", 
        "Ward", "Métis", "Ma mère", "Vas-y", "Cheerios", "La Fleur aux dent", "Chavez", "Perez", "Gomez", "Martinez", 
        "Vazquez", "Cortez", "Hernandez", "Juarez", "Lopez", "Mez", "Lucas", "Jonas", "Thomas", "Nicholas", "Elias", 
        "Tobias", "Zacharias", "Silas", "Pascal", "Mathias"
    ]

    names = [ent.text for ent in doc.ents if ent.label_ == 'PER']
    unique_names = set(names)
    replaced_names = []
    log = {}

    for name in unique_names:
        if name in exception_names:
            continue  # Skip the replacement for exception names

        # Check if the word after the name starts with a capital letter
        next_token_index = doc.text.find(name) + len(name)
        if next_token_index < len(doc.text):
            next_token = doc.text[next_token_index:].split()[0]
            if next_token and not next_token[0].isupper():
                continue  # Skip if the next token is not capitalized

        for suffix, replacement in name_replacements.items():
            if name.endswith(suffix):
                new_name = name[:-len(suffix)] + replacement
                text = text.replace(name, new_name)
                replaced_names.append(new_name)
                log[name] = new_name
                break

    return text, log

# Function to clean text (removing extra spaces, tabs, and control characters after punctuation)
def clean_text(text):
    # Remove trailing spaces at the end of each line without merging paragraphs
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)

    # Remove non-standard characters (tabs, newlines, control characters like \x07)
    text = re.sub(r'[\t\x07]', '', text)  # Explicitly remove any tabs or control characters

    # Remove any extra spaces after punctuation like ".", "!", "?" or after numbers
    text = re.sub(r'([.!?:])\s*\n\s+', r'\1\n', text)  # Ensure punctuation stays on the correct line

    # Remove unnecessary spaces between lines and words
    text = re.sub(r'[ \t]+(?=\n)', '', text)  # Remove any spaces before a new line

    return text

# Function to process text files and log replacements
def process_text_file(input_file_path, output_file_path, log_file_path, word_count):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Replace names and log them
    cleaned_text, replacements_log = extract_and_replace_names(text)

    # Clean up free spaces and control characters after a word
    cleaned_text = clean_text(cleaned_text)

    # Write the cleaned text to the output file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_text)

    # Log the name replacements
    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        for original, replacement in replacements_log.items():
            log_file.write(f"{original}: {replacement}\n")

    # Count words and add to the total word count
    word_count += len(cleaned_text.split())
    return word_count

if __name__ == "__main__":
    input_directory = os.path.join("../", "txt_processed/8-s_back_")
    output_directory = os.path.join("../", "txt_processed/9-names_correction")
    log_directory = os.path.join(output_directory, 'logs_')

    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(log_directory, exist_ok=True)

    total_word_count = 0

    for file_name in os.listdir(input_directory):
        if file_name.endswith('.txt'):
            input_file_path = os.path.join(input_directory, file_name)
            output_file_path = os.path.join(output_directory, file_name)
            log_file_name = f"log_{file_name}"
            log_file_path = os.path.join(log_directory, log_file_name)

            print(f"Processing {file_name}...")
            total_word_count = process_text_file(input_file_path, output_file_path, log_file_path, total_word_count)
            print(f"Processed file saved as {file_name}")
            print(f"Log saved as {log_file_name}")

    # Save total word count to num_words.txt
    num_words_file_path = os.path.join(log_directory, 'num_words.txt')
    with open(num_words_file_path, 'w', encoding='utf-8') as num_words_file:
        num_words_file.write(f"Total word count: {total_word_count}\n")

    print(f"Total word count: {total_word_count}")

    # Generate the EPUB3 file
    #generate_epub(output_directory, log_directory)

    print("Script completed")
