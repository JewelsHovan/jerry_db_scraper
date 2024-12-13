"""
Scrapes each event detailed page 

loading the events data 
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
from typing import Dict, Any
import copy
from tqdm import tqdm
import logging
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='scraping.log'
)

async def extract_event_data(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
    """
    Asynchronously extract data from an event page
    """
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            content = await response.text()
            
        soup = BeautifulSoup(content, 'html.parser')
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

    except Exception as e:
        logging.error(f"Error processing {url}: {str(e)}")
        return None

async def process_events_data(input_file: str, output_file: str, max_concurrent: int = 10, delay_before_request: float = 0.2, checkpoint_interval: int = 500) -> None:
    """
    Asynchronously process all events with a progress bar and checkpointing
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file
        max_concurrent: Maximum number of concurrent requests
        delay_before_request: Delay between requests
        checkpoint_interval: Number of events to process before saving checkpoint
    """
    # Create checkpoints directory if it doesn't exist
    checkpoint_dir = "checkpoints"
    os.makedirs(checkpoint_dir, exist_ok=True)

    # Load from latest checkpoint if exists, otherwise load original data
    checkpoint_files = sorted([f for f in os.listdir(checkpoint_dir) if f.startswith('checkpoint_')])
    
    if checkpoint_files:
        latest_checkpoint = os.path.join(checkpoint_dir, checkpoint_files[-1])
        logging.info(f"Loading from checkpoint: {latest_checkpoint}")
        with open(latest_checkpoint, 'r') as f:
            updated_data = json.load(f)
    else:
        with open(input_file, 'r') as f:
            data = json.load(f)
        updated_data = copy.deepcopy(data)

    # Create semaphore for rate limiting
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # Collect all events that need processing
    events_to_process = []
    for year, events in data.items():
        if not isinstance(events, list):
            continue
        for i, event in enumerate(events):
            if 'url' in event:
                events_to_process.append((year, i, event))

    async with aiohttp.ClientSession() as session:
        # Create progress bar
        pbar = tqdm(total=len(events_to_process), desc="Processing events")
        
        processed_count = 0
        
        # Process events with semaphore
        async def process_event(year: str, index: int, event: Dict[str, Any]):
            nonlocal processed_count
            async with semaphore:
                try:
                    await asyncio.sleep(delay_before_request)
                    detailed_data = await extract_event_data(session, event['url'])
                    if detailed_data:
                        updated_data[year][index] = {**event, **detailed_data}
                    
                    processed_count += 1
                    
                    # Save checkpoint every checkpoint_interval events
                    if processed_count % checkpoint_interval == 0:
                        checkpoint_file = os.path.join(
                            checkpoint_dir, 
                            f'checkpoint_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                        )
                        logging.info(f"Saving checkpoint after {processed_count} events: {checkpoint_file}")
                        with open(checkpoint_file, 'w') as f:
                            json.dump(updated_data, f, indent=2)
                        
                        # Remove old checkpoints (keep last 3)
                        checkpoint_files = sorted([f for f in os.listdir(checkpoint_dir) if f.startswith('checkpoint_')])
                        for old_checkpoint in checkpoint_files[:-3]:
                            os.remove(os.path.join(checkpoint_dir, old_checkpoint))
                            
                except Exception as e:
                    logging.error(f"Failed to process {event['url']}: {str(e)}")
                finally:
                    pbar.update(1)

        # Create tasks for all events
        tasks = [
            process_event(year, i, event) 
            for year, i, event in events_to_process
        ]
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        pbar.close()
    
    # Save updated data
    with open(output_file, 'w') as f:
        json.dump(updated_data, f, indent=2)

def main():
    input_file = "event_data.json"
    output_file = "event_data_detailed.json"

    # scrape params
    MAX_CONCURRENT = 10
    DELAY_BEFORE_REQUEST = 0.2
    CHECKPOINT_INTERVAL = 1000
    
    # Run async process
    asyncio.run(process_events_data(input_file, 
                                    output_file, 
                                    max_concurrent=MAX_CONCURRENT, 
                                    delay_before_request=DELAY_BEFORE_REQUEST, 
                                    checkpoint_interval=CHECKPOINT_INTERVAL))

if __name__ == "__main__":
    main()