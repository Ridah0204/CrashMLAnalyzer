import os
import pandas as pd
from PyPDF2 import PdfReader
from tkinter import Tk, filedialog

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file, including encrypted ones."""
    try:
        reader = PdfReader(pdf_path)

        # Check if the PDF is encrypted
        if reader.is_encrypted:
            try:
                reader.decrypt("")  # Try decrypting with an empty password
            except Exception as e:
                print(f"Failed to decrypt {pdf_path}: {e}")
                return None

        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

def save_to_csv(data, output_file):
    """Saves extracted data to a CSV file."""
    df = pd.DataFrame({'Extracted Text': [data]})
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

def main():
    """Main function to upload a folder and process all PDFs."""
    Tk().withdraw()
    folder_path = filedialog.askdirectory(title="Select a Folder Containing PDFs")
    
    if not folder_path:
        print("No folder selected. Exiting.")
        return
    
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in the selected folder.")
        return
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        text = extract_text_from_pdf(pdf_path)
        if text:
            output_csv = os.path.splitext(pdf_path)[0] + ".csv"
            save_to_csv(text, output_csv)
        else:
            print(f"No text extracted from {pdf_file}.")

if __name__ == "__main__":
    main()
