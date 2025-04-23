import pandas as pd
from urllib.request import urlopen, Request
from io import BytesIO
from PyPDF2 import PdfReader
import logging
import time
import requests
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


def download_and_process_pdf(url, max_retries=3, backoff_factor=1.5):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            memoryFile = BytesIO(response.content)
            reader = PdfReader(memoryFile)
            filtered_text_data = {k: v["/V"] for k, v in reader.get_fields().items()
                                if isinstance(v, dict) and "/V" in v.keys()}

            return pd.DataFrame([filtered_text_data])
        except RequestException as e:
            wait_time = backoff_factor ** retries
            logging.warning(f"Attempt {retries+1} failed: {e}. Retrying in {wait_time:.1f} seconds...")
            time.sleep(wait_time)
            retries += 1
        except Exception as e:
            logging.error(f"Failed to process PDF from {url}: {e}")
            return None
    
    logging.error(f"Failed to download PDF from {url} after {max_retries} attempts")
    return None

# Define a list of URLs for your PDF files
urls = [
    
    "https://www.dmv.ca.gov/portal/file/zoox_01012024b-pdf/",
]

# Create an empty list to store DataFrames from each URL
data_frames = []

for url in urls:
    df = download_and_process_pdf(url)
    if df is not None:
        data_frames.append(df)

# Combine all DataFrames into a single DataFrame
if data_frames:
    combined_df = pd.concat(data_frames, ignore_index=True)
    print(combined_df)

    # Save to CSV
    csv_filename = "extracted_pdf_data.csv"
    combined_df.to_csv(csv_filename, index=False)
    print(f"Data successfully saved to {csv_filename}")
else:
    print("No data was extracted from the PDFs.")