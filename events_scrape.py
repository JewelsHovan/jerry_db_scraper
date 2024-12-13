"""
Scrapes each event detailed page 

loading the events data 
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from typing import Dict, Any
import copy

def extract_event_data(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes

    soup = BeautifulSoup(response.content, 'html.parser')

    event_data = {}

    # Event Date (and indication of placeholder)
    event_data['date_from_title'] = soup.title.text.split(" ")[0]
    h4_date = soup.find('h4', style='display: inline;')
    event_data['date'] = h4_date.text.strip() if h4_date else None
    placeholder_text = soup.find('span', class_='text-muted')
    event_data['date_is_placeholder'] = placeholder_text.text.strip() if placeholder_text else "Date might be accurate"

    # Event Name/Band
    event_data['band'] = soup.title.text.split(" ", 1)[1]

    # Venue
    venue_h4 = soup.find('h4', string=lambda text: text and (
        "Analy High School" in text or 
        "Warfield Theatre" in text
    ))
    event_data['venue'] = venue_h4.text.strip() if venue_h4 else None

    # Setlist
    setlist = []
    partial_set_div = soup.find('div', id='simple-card')
    if partial_set_div:
        song_links = partial_set_div.find_all('a', class_='')
        for song_link in song_links:
            setlist.append(song_link.text.strip())
    
    if not setlist:
        table_setlist = soup.find('table', id=lambda x: x and x.startswith('datatable_'))
        if table_setlist:
            for row in table_setlist.find_all('tr'):
                song_cell = row.find('a')
                if song_cell:
                    setlist.append(song_cell.text.strip())
    
    event_data['setlist'] = setlist

    # Musicians
    musicians_div = soup.find('div', id='musicians-content')
    musicians = []
    if musicians_div:
        lines = musicians_div.get_text(strip=True).splitlines()
        i = 0
        while i < len(lines):
            musician_name = lines[i]
            if i + 1 < len(lines):
                instrument = lines[i + 1].strip('- ')
                musicians.append({'name': musician_name, 'instrument': instrument})
                i += 2
            else:
                musicians.append({'name': musician_name, 'instrument': 'unknown'})
                i += 1
    event_data['musicians'] = musicians

    # Notes
    notes_container = soup.find('div', class_='notes-container')
    notes = []
    if notes_container:
        for li in notes_container.find_all('li'):
            notes.append(li.text.strip())
    event_data['notes'] = notes

    return event_data

def process_events_data(input_file: str, output_file: str) -> None:
    """
    Read event_data.json, fetch detailed data for each event, and create updated JSON file
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file
    """
    # Load original JSON data
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Create deep copy to modify
    updated_data = copy.deepcopy(data)
    
    # Process each year
    for year, events in data.items():
        print(f"Processing year {year}...")
        
        # Skip if not a list of events
        if not isinstance(events, list):
            continue
            
        # Process each event
        for i, event in enumerate(events):
            if 'url' not in event:
                continue
                
            try:
                # Get detailed event data
                detailed_data = extract_event_data(event['url'])
                
                # Update event with detailed data while preserving original fields
                updated_event = {**event, **detailed_data}
                updated_data[year][i] = updated_event
                
                # Status update
                print(f"Processed {event['url']}")
                
                # Polite delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing {event['url']}: {str(e)}")
                continue
    
    # Save updated data
    with open(output_file, 'w') as f:
        json.dump(updated_data, f, indent=2)

def main():
    input_file = "event_data.json"
    output_file = "event_data_detailed.json"
    
    process_events_data(input_file, output_file)

if __name__ == "__main__":
    main()