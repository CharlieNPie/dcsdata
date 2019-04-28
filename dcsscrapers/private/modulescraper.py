import os, re
from bs4 import BeautifulSoup
from . import scraperclass
import requests, requests.exceptions

HEADINGS = ["module code", "module name", "summary", "session", "credits", "assessment", 
    "lecturer", "aims", "objectives", "content", "teaching method", "feedback"]

DATA_DIR = "modules"
PAGE_URL = "http://www.dcs.shef.ac.uk/intranet/teaching/public/modules/2019-20/"

def scrape_module(full_path, cols):
    """
    Retrieves Computer Science module data from the University of Sheffield website.

    Args:
        full_path: Path of the local data directory used if connection fails
        cols: List of module data that has already been scraped. Data is appended to this list. 

    Returns:
        cols: cols argument with newly-scraped data appended to it.

    """

    #get only the html filename from path string
    path_directories = full_path.split("/")
    url_attach = path_directories[-2] + "/" + path_directories[-1]

    scrape_url = PAGE_URL + url_attach

    #makes request to profile page
    try:
        page_request = requests.get(scrape_url)
        page_request.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError):
        print("No viable connection at this time. Using local storage instead...")
        with open(full_path, encoding="utf8") as file:
            html = BeautifulSoup(file, "lxml")    
    else:
        html = BeautifulSoup((page_request.content), "lxml")

    table = html.find("table", {"id" : "contentContainer"})

    #get string containing course code and title and split up into list
    course_title = table.find("h2").getText()
    code_and_title = course_title.split(" ", 1)

    #append module names and codes to respective columns
    cols[HEADINGS.index("module code")][1].append(code_and_title[0])
    cols[HEADINGS.index("module name")][1].append(code_and_title[1])

    table_body = table.find("tbody")

    rows = table_body.find_all("tr")
    for row in rows:
        if not row.find("th"):
            continue
        column_head = row.find("th").getText()
        column_data = row.find("td").getText()
        for heading in HEADINGS[2:]:
            if heading in column_head.lower():
                column_text = column_data.strip().replace("\n", "")
                column_text = column_text.replace("\r", "")
                column_text = column_text.replace("\u200b", "")
                column_text = re.sub("[ ]{2,}", " ", column_text)
                cols[HEADINGS.index(heading)][1].append(column_text.strip())
    
    for heading in HEADINGS[2:]:
        if heading not in table_body.getText().lower():
            cols[HEADINGS.index(heading)][1].append(None)

    return cols

SCRAPER = scraperclass.Scraper(
    "modules",
    lambda a, b : scrape_module(a, b), 
    DATA_DIR, 
    HEADINGS,
    )