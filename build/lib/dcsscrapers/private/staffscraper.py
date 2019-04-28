import os, re
from bs4 import BeautifulSoup
from . import scraperclass
import requests, requests.exceptions

HEADINGS = ["firstname", "surname", "telephone", "email", "researchgroup", "biography"]

PAGE_URL = "https://www.sheffield.ac.uk/dcs/people/academic/"
DATA_DIR = "academic"

#helper function for regex search
def regex_search(regex, text):
    """
    Searches a body of text to see if it matches a regex query.

    Args:
        regex: a regex query in string form
        text: the text to be searched through

    Returns:
        return_value: If the search is successful then return the string matching the query. If not,
        return a null value. 

    """
    search_item = re.search(regex, text)
    return_value = search_item.group() if search_item else None
    return return_value

#method to scrape each staff member
def scrape_staff_member(full_path, cols):
    """
    Retrieves Computer Science staff data from the University of Sheffield website.

    Args:
        full_path: Path of the local data directory used if connection fails
        cols: List of module data that has already been scraped. Data is appended to this list. 

    Returns:
        cols: cols argument with newly-scraped data appended to it.
    
    """

    #constructs page URL for path supplied
    path_directories = full_path.split("/")
    url_attach = path_directories[-1]
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

    #html = BeautifulSoup(open(full_path, encoding="utf8"), 'lxml')

    #find table relevant to staff member and extract text
    table = html.find("table", {"class" : "layout"})
    table_text = table.get_text().strip().replace("\n", " ")

    #Staff name 
    staff_name = table.h2.get_text()
    remove_title = re.sub("(Emeritus )?(((D|M)r)|Prof([.]|essor)?)", "", staff_name).strip()
    split = remove_title.split(' ', 1)
    cols[0][1].append(split[0])
    cols[1][1].append(split[1])

    #Phone numbers
    search_phone = regex_search('[+](.+?)\d{4}', table_text)
    cols[2][1].append(search_phone[:20]) if search_phone else cols[2][1].append(search_phone)

    #Email
    email = regex_search('(\S*[.]\S*@sheffield.ac.uk)', table_text)
    cols[3][1].append(email)

    #Research Group
    research_grp = regex_search('((M|m)ember|(H|h)ead) of the.*(r|R)esearch (g|G)roups?', table_text)
    cols[4][1].append(research_grp)

    #Biography
    bio_table = html.find("table", {"class" : "cms-tabs"})
    cols[5][1].append(bio_table.find("p").get_text()) if bio_table else cols[5][1].append(None)

    return(cols)


SCRAPER = scraperclass.Scraper(
    "staff",
    lambda a, b : scrape_staff_member(a, b), 
    DATA_DIR, 
    HEADINGS
    )

