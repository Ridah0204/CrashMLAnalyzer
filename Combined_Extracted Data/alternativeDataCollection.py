import pandas as pd
import os
import glob
from PyPDF2 import PdfReader
import logging
from tqdm import tqdm  # For progress bar
#C:\Users\ridah\Desktop\from desktop to new pc\sENIOR rESEARCH pROJECT\pdf Extraction\pdf_extraction\reports_2019
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_pdf(file_path):
    """
    Processes a local PDF file and extracts form field data.
    
    Args:
        file_path: Path to the local PDF file
        
    Returns:
        DataFrame with the extracted data or None if processing failed
    """
    try:
        # Get filename to use as identifier in the output
        filename = os.path.basename(file_path)
        
        # Process the PDF
        reader = PdfReader(file_path)
        
        # Check if the PDF has form fields
        if not reader.get_fields():
            logging.warning(f"No form fields found in {filename}")
            return None
            
        # Extract form field data
        filtered_text_data = {k: v["/V"] for k, v in reader.get_fields().items()
                             if isinstance(v, dict) and "/V" in v.keys()}
        
        # Add filename as a column so we know which file each row came from
        filtered_text_data['source_filename'] = filename
        
        return pd.DataFrame([filtered_text_data])
    
    except Exception as e:
        logging.error(f"Failed to process PDF {file_path}: {e}")
        return None

def main():
    # Directory containing PDF files
    pdf_directory = input("Enter the directory path containing your PDF files: ").strip()
    
    # Verify the directory exists
    if not os.path.isdir(pdf_directory):
        logging.error(f"Directory not found: {pdf_directory}")
        return
    
    # Get all PDF files in the directory
    pdf_files = glob.glob(os.path.join(pdf_directory, "*.pdf"))
    
    if not pdf_files:
        logging.error(f"No PDF files found in {pdf_directory}")
        return
    
    logging.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF file
    data_frames = []
    
    # Use tqdm for a progress bar
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        df = process_pdf(pdf_file)
        if df is not None:
            data_frames.append(df)
    
    # Combine all DataFrames into a single DataFrame
    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True)
        logging.info(f"Successfully processed {len(data_frames)} out of {len(pdf_files)} files")
        
        # Save to CSV
        csv_filename = os.path.join(pdf_directory, "extracted_pdf_data_2024.csv")
        combined_df.to_csv(csv_filename, index=False)
        logging.info(f"Data successfully saved to {csv_filename}")
        
        # Display a sample of the data
        logging.info("Sample of extracted data:")
        print(combined_df.head())
        
        # Report on columns found
        logging.info(f"Columns extracted: {', '.join(combined_df.columns)}")
    else:
        logging.error("No data was successfully extracted from any of the PDFs")

if __name__ == "__main__":
    main()





# Example PDF directory path:
# C:\\Users\\ridah\\Desktop\\from desktop to new pc\\sENIOR rESEARCH pROJECT\\pdf Extraction\\pdf_extraction\\reports_2019