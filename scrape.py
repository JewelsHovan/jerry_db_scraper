import requests
from urllib.parse import urljoin
import time
from bs4 import BeautifulSoup
import json

def get_year_options():
    """
    Fetch webpage and extract year options from the select element
    
    Returns:
        list: List of year values
    """
    # Fetch the webpage
    response = requests.get(base_url)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the select element by its id
    select_element = soup.find('select', id='year-select')
    
    # Extract all option values
    years = [option['value'] for option in select_element.find_all('option')]
    
    return years

def get_event_links_for_year(year):
    """
    Fetch all event links for a specific year
    
    Args:
        year (str): Year to fetch events for
        
    Returns:
        list: List of event URLs
    """
    year_url = f"{base_url}?year={year}"
    print(f"Fetching events for {year} from {year_url}")
    response = requests.get(year_url)
    response.raise_for_status()
    
    return extract_links_from_html(response.text, base_url)

def extract_links_from_html(html_content, base_url):
    """
    Extracts event information from HTML content and constructs event data objects.

    Args:
        html_content (str): The HTML content as a string.
        base_url (str): The base URL to use for constructing full URLs.

    Returns:
        list: A list of event dictionaries containing URL, date, venue, band, and other info
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the events table
        table = soup.find('table', id='datatable_events')
        if not table:
            return []
            
        events = []
        
        # Process each row in the table body
        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 7:  # Ensure we have all needed cells
                event = {
                    'date': cells[0].find('span').text.strip() if cells[0].find('span') else '',
                    'url': urljoin(base_url, cells[0].find('a')['href']) if cells[0].find('a') else '',
                    'venue': {
                        'name': cells[1].text.strip(),
                        'url': urljoin(base_url, cells[1].find('a')['href']) if cells[1].find('a') else ''
                    },
                    'band': {
                        'name': cells[2].text.strip(),
                        'url': urljoin(base_url, cells[2].find('a')['href']) if cells[2].find('a') else ''
                    },
                    'songs': cells[3].text.strip(),
                    'category': cells[4].text.strip(),
                    'act_type': cells[5].text.strip(),
                    'show_id': cells[6].text.strip()
                }
                events.append(event)
        
        return events
        
    except Exception as e:
        print(f"Error extracting event data: {e}")
        return []

if __name__ == "__main__":
    # PARAMS
    base_url = "https://jerrybase.com/events"
    output_file = "event_data.json"  # Changed to .json extension

    # Execute and print results
    try:
        years = get_year_options()
        print("Available years:", years)
        
        # Fetch event data for each year
        all_event_data = {}
        for i, year in enumerate(years):
            if i >= 5:
                break  # Limit to 5 iterations for testing
            print(f"Fetching events for {year}...")
            events = get_event_links_for_year(year)
            all_event_data[year] = events
            print(f"Found {len(events)} events for {year}")
            time.sleep(0.2)  # Add a delay to avoid overwhelming the server
            
        # Save results to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_event_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nEvent data has been saved to {output_file}")
            
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    except AttributeError as e:
        print(f"Error parsing HTML: {e}")
    except IOError as e:
        print(f"Error writing to file: {e}")

    # Print summary of all events found
    print("\nSummary of events found:")
    for year, events in all_event_data.items():
        print(f"{year}: {len(events)} events")

