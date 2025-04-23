from io import BytesIO
from pypdf import PdfReader
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def process_local_pdf(file_path):
    """
    Processes a local PDF file, extracts form field data, and returns a DataFrame.
    
    Args:
        file_path: The path to the local PDF file.
        
    Returns:
        A pandas DataFrame containing the extracted data or None if failed
    """
    try:
        reader = PdfReader(file_path)
        
        # Extract form fields
        try:
            fields = reader.get_fields()
            if fields:
                filtered_text_data = {k: v["/V"] for k, v in fields.items() 
                                    if isinstance(v, dict) and "/V" in v.keys()}
                
                # Add filename as a column to help track the source
                result_df = pd.DataFrame([filtered_text_data])
                result_df['source_file'] = os.path.basename(file_path)
                
                return result_df
            else:
                logging.warning(f"No form fields found in {file_path}")
                return None
        except Exception as e:
            logging.error(f"Error extracting form fields from {file_path}: {e}")
            return None
            
    except Exception as e:
        logging.error(f"Failed to process PDF {file_path}: {e}")
        return None

def process_pdf_directory(directory_path):
    """
    Processes all PDF files in the specified directory.
    
    Args:
        directory_path: Path to the directory containing PDF files.
        
    Returns:
        A pandas DataFrame containing combined data from all PDFs.
    """
    data_frames = []
    
    # Get list of all PDF files in the directory
    pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logging.warning(f"No PDF files found in {directory_path}")
        return None
    
    # Process each PDF file
    for pdf_file in pdf_files:
        file_path = os.path.join(directory_path, pdf_file)
        logging.info(f"Processing {file_path}")
        
        df = process_local_pdf(file_path)
        if df is not None:
            data_frames.append(df)
        
    # Combine all DataFrames into a single DataFrame
    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True)
        return combined_df
    else:
        logging.warning("No data was extracted from any of the PDFs.")
        return None

# Example usage
if __name__ == "__main__":
    # Set the directory path where your PDFs are stored
    pdf_directory = "C:\\Users\\ridah\\Desktop\\from desktop to new pc\\sENIOR rESEARCH pROJECT\\pdf Extraction\\pdf_extraction\\reports_2024"  # Change this to your actual directory path
    
    # Process all PDFs in the directory
    result_df = process_pdf_directory(pdf_directory)
    
    if result_df is not None:
        print(f"Successfully processed {len(result_df)} PDF files.")
        print(result_df)
        
        # Save to CSV
        output_file = "extracted_pdf_data_22024.csv"
        result_df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")
    else:
        print("No data was extracted from the PDFs.")