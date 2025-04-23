import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin
import logging
from tqdm import tqdm
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_file(url, destination_folder, filename=None):
    """
    Download a file from a URL to a specified folder
    
    Args:
        url: URL of the file to download
        destination_folder: Folder to save the file to
        filename: Optional custom filename
        
    Returns:
        Path to the downloaded file or None if download failed
    """
    try:
        # Create destination folder if it doesn't exist
        os.makedirs(destination_folder, exist_ok=True)
        
        # Get filename from URL if not provided
        if filename is None:
            filename = url.split('/')[-1]
        
        file_path = os.path.join(destination_folder, filename)
        
        # Check if file already exists
        if os.path.exists(file_path):
            logging.info(f"File already exists: {file_path}")
            return file_path
        
        # Download the file
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, stream=True, timeout=60, headers=headers)
        response.raise_for_status()
        
        # Get total file size for progress bar
        total_size = int(response.headers.get('content-length', 0))
        
        # Download with progress
        with open(file_path, 'wb') as f, tqdm(
                desc=filename,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                bar.update(size)
        
        return file_path
    
    except Exception as e:
        logging.error(f"Failed to download {url}: {e}")
        # Sleep for a moment before returning to avoid hammering the server if there's an issue
        time.sleep(2)
        return None

def extract_year_from_url_or_text(url, text):
    """Extract year from URL or text content"""
    # Try to find a year pattern in the URL
    url_year_match = re.search(r'(20[0-9]{2})', url)
    if url_year_match:
        return url_year_match.group(1)
    
    # Try to find a year pattern in the text
    text_year_match = re.search(r'(20[0-9]{2})', text or '')
    if text_year_match:
        return text_year_match.group(1)
    
    return None

def get_report_links(url):
    """
    Scrape the DMV website for collision report links
    
    Args:
        url: URL of the DMV autonomous vehicle collision reports page
        
    Returns:
        Dictionary with year as key and list of report URLs as value
    """
    try:
        # Add a user agent to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Dictionary to store reports by year
        reports_by_year = {year: [] for year in range(2019, 2025)}
        
        # Based on the screenshot, we now know the structure:
        # Find all div elements with accordion content that contain lists of reports
        year_sections = soup.find_all('div', class_=re.compile(r'accordion-block_content'))
        
        for section in year_sections:
            # Find the year heading near this section
            year_heading = section.find_previous(re.compile(r'h\d'))
            year = None
            
            if year_heading:
                year_match = re.search(r'(20[0-9]{2})', year_heading.get_text())
                if year_match:
                    year = int(year_match.group(1))
            
            # Find all PDF links in this section
            list_items = section.find_all('li')
            
            for li in list_items:
                # Find the anchor tag for the PDF
                pdf_links = li.find_all('a', href=re.compile(r'\.pdf', re.IGNORECASE))
                
                for link in pdf_links:
                    href = link.get('href')
                    # Make sure we have the full URL
                    full_url = urljoin(url, href)
                    link_text = link.get_text().strip()
                    
                    # If we couldn't determine the year from the heading, try from URL or link text
                    if not year:
                        extracted_year = extract_year_from_url_or_text(full_url, link_text)
                        if extracted_year:
                            year = int(extracted_year)
                    
                    # If we have a valid year and it's in our range, add the link
                    if year and 2019 <= year <= 2024:
                        reports_by_year[year].append({
                            'url': full_url,
                            'text': link_text
                        })
        
        # If we couldn't find links with the above approach, try a more general approach
        if all(len(links) == 0 for links in reports_by_year.values()):
            logging.warning("Could not find reports using the expected structure. Trying a more general approach.")
            
            # Find all lists that might contain reports
            list_elements = soup.find_all('ul', class_=re.compile(r'wp-block-list'))
            
            for ul in list_elements:
                # Find all PDF links
                links = ul.find_all('a', href=re.compile(r'\.pdf', re.IGNORECASE))
                
                for link in links:
                    href = link.get('href')
                    full_url = urljoin(url, href)
                    link_text = link.get_text().strip()
                    
                    # Extract year from URL or link text
                    extracted_year = extract_year_from_url_or_text(full_url, link_text)
                    
                    if extracted_year and 2019 <= int(extracted_year) <= 2024:
                        reports_by_year[int(extracted_year)].append({
                            'url': full_url,
                            'text': link_text
                        })
        
        # One more fallback if we still didn't find links
        if all(len(links) == 0 for links in reports_by_year.values()):
            logging.warning("Still couldn't find reports. Trying a final approach to find any PDF links.")
            
            # Find all PDF links on the page
            all_links = soup.find_all('a', href=re.compile(r'\.pdf', re.IGNORECASE))
            
            for link in all_links:
                href = link.get('href')
                full_url = urljoin(url, href)
                link_text = link.get_text().strip()
                
                # Try to determine the year
                extracted_year = extract_year_from_url_or_text(full_url, link_text)
                
                if extracted_year and 2019 <= int(extracted_year) <= 2024:
                    reports_by_year[int(extracted_year)].append({
                        'url': full_url,
                        'text': link_text
                    })
                elif 'collision' in href.lower() or 'collision' in link_text.lower():
                    # If we can't determine the year but it's a collision report, 
                    # add it to the "most recent" year
                    most_recent_year = max(year for year in range(2019, 2025) 
                                         if year in reports_by_year)
                    reports_by_year[most_recent_year].append({
                        'url': full_url,
                        'text': link_text
                    })
        
        # Log how many reports we found for each year
        for year, links in reports_by_year.items():
            if links:
                logging.info(f"Found {len(links)} reports for year {year}")
            else:
                logging.warning(f"No reports found for year {year}")
        
        return reports_by_year
    
    except Exception as e:
        logging.error(f"Failed to get report links: {e}")
        return {year: [] for year in range(2019, 2025)}

def main():
    # URL of the DMV autonomous vehicle collision reports page
    url = "https://www.dmv.ca.gov/portal/vehicle-industry-services/autonomous-vehicles/autonomous-vehicle-collision-reports/"
    
    # Base directory for saving reports
    base_dir = input("Enter the directory where you want to save the reports: ").strip()
    
    # Get all report links
    logging.info("Fetching report links from the DMV website...")
    reports_by_year = get_report_links(url)
    
    # Count total reports
    total_reports = sum(len(links) for links in reports_by_year.values())
    logging.info(f"Found a total of {total_reports} reports across all years")
    
    if total_reports == 0:
        logging.error("No reports found. Please check the website structure or try again later.")
        return
    
    # Download all reports
    downloaded_count = 0
    
    for year, links in reports_by_year.items():
        if not links:
            continue
            
        # Create year directory
        year_dir = os.path.join(base_dir, f"reports_{year}")
        
        logging.info(f"Downloading {len(links)} reports for year {year}...")
        for i, link_data in enumerate(links):
            link_url = link_data['url']
            link_text = link_data['text']
            
            # Try to create a descriptive filename from the link text
            # Remove special characters and replace spaces with underscores
            clean_text = re.sub(r'[^\w\s-]', '', link_text).strip().lower()
            clean_text = re.sub(r'[\s]+', '_', clean_text)
            
            # If the clean text is empty or too short, use a default name
            if len(clean_text) < 5:
                filename = f"report_{year}_{i+1}.pdf"
            else:
                filename = f"{clean_text}.pdf"
                
                # Make sure filename ends with .pdf
                if not filename.lower().endswith('.pdf'):
                    filename += '.pdf'
            
            # Download the file
            result = download_file(link_url, year_dir, filename)
            
            if result:
                downloaded_count += 1
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(1)
    
    logging.info(f"Download complete. Successfully downloaded {downloaded_count} out of {total_reports} reports.")

if __name__ == "__main__":
    main()