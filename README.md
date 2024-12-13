# Jerry Garcia Concert Database Scraper

A Python-based scraper for collecting and organizing Jerry Garcia's concert history from jerrybase.com. This tool captures detailed information about performances spanning from pre-1965 through 1968, including the Grateful Dead, Warlocks, and various side projects.

## Overview

This project provides tools to:
1. Fetch basic concert listings (`scrape.py`)
2. Enhance concert data with detailed information (`events_scrape.py`)

## Data Structure

The scraped data is stored in JSON format with two main files:

### event_data.json
Contains basic concert information organized by year:
```json
{
  "pre-1965": [
    {
      "date": "1959-10-00 [Thu]",
      "url": "https://jerrybase.com/events/19591001-01",
      "venue": {
        "name": "Analy High School, Sebastopol, CA",
        "url": "https://jerrybase.com/venues/1133"
      },
      "band": {
        "name": "The Chords",
        "url": "https://jerrybase.com/acts/the-chords"
      },
      "songs": "Partial Set: Raunchy",
      "category": "Public",
      "act_type": "Side-Project",
      "show_id": "19591001_1133"
    }
  ]
}
```

### event_data_detailed.json
Enhanced version including additional details for each show:
- Setlists
- Musicians and their instruments
- Notes and historical context
- Date verification information

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/jerry-garcia-db-scraper.git

# Install requirements
pip install -r requirements.txt
```

## Usage

1. First, collect basic concert data:
```bash
python scrape.py
```

2. Then, enhance the data with detailed information:
```bash
python events_scrape.py
```

## Configuration

Key parameters in `events_scrape.py`:
- `MAX_CONCURRENT`: Number of concurrent requests (default: 10)
- `DELAY_BEFORE_REQUEST`: Delay between requests in seconds (default: 0.2)

## Data Fields

- `date`: Concert date (YYYY-MM-DD format)
- `venue`: Performance location details
- `band`: Performing group name
- `songs`: Setlist information
- `category`: Event type (Public/Private/Canceled)
- `act_type`: Performance category (GD/Side-Project)
- `show_id`: Unique identifier for the show
- `musicians`: List of performers and their instruments (in detailed version)
- `notes`: Additional context and historical information (in detailed version)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Data sourced from jerrybase.com, a comprehensive database of Jerry Garcia's performances.

## Note

Please be respectful of the source website's resources and follow their terms of service when using this scraper.