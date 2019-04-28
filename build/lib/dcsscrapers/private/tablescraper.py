from bs4 import BeautifulSoup
from . import scraperclass
import pandas as pd
import requests, requests.exceptions

DATA_DIR = "timetable"
HEADINGS = ["unit code", "unit title", "group", "activity", "day", "start time", "end time", 
    "university weeks", "room no", "location", "lecturer"]

def scrape_table(full_path, cols):
    """
    Scrapes timetable from a given HTML file. 

    Args:
        full_path:
        cols:

    Returns:
        cols: 
        
    """

    page_url = "http://www-online.shef.ac.uk:3001/pls/live/web_tt.timetable?dept_code=COM&dept_name=Computer+Science"

    # Makes GET request to webpage.
    # If request is successful, pull content directly from page. If not, use local file.
    try:
        page_request = requests.get(page_url)
        page_request.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError):
        print("No viable connection at this time. Using local storage instead...")
        with open(full_path) as file:
            html = BeautifulSoup(file, "lxml")    
    else:
        html = BeautifulSoup(page_request.content, "lxml")

    # finds timetable identifier and gets table headings
    table = html.find("div", {"title" : "Timetable"})

    # finds all table data rows after the initial headings
    rows = table.find_all("tr")[1:]

    # iterates through rows and adds column data to cols array
    for row in rows:
        i = 0
        columns = row.find_all("td")
        for column in columns:
            columntext = column.get_text().strip()
            cols[i][1].append(columntext)
            i += 1

    return cols

SCRAPER = scraperclass.Scraper(
    "timetables",
    lambda a, b : scrape_table(a, b),
    DATA_DIR,
    HEADINGS
)