import os, sys, re
from enum import Enum
from bs4 import BeautifulSoup
import pandas as pd
from pandas.io import sql
from .private import staffscraper, modulescraper, tablescraper, scraperclass
from sqlalchemy import create_engine
import sqlalchemy.engine.url as url
from sqlalchemy.exc import OperationalError
import MySQLdb

class ScraperData(Enum):
    """
    Enums to access Scraper objects for staff, modules and timetables.

    """
    STAFF = staffscraper.SCRAPER
    MODULES = modulescraper.SCRAPER
    TIMETABLES = tablescraper.SCRAPER


def get_data(scraper):
    """
    Scrapes data from a given set of HTML documents. 


    Args:
        scraper: A Scraper object containing the appropriate scraping method, name of the data folder and the data headings.


    Returns:
        dataframe: A pandas dataframe containing the scraped data in a tabulated format. 

    Raises:
        TypeError: Raised if the scraper argument provided to the method is not a Scraper object.

    """

    if not isinstance(scraper, scraperclass.Scraper):
        raise TypeError("Argument provided is not a Scraper class object.")

    data_dir = scraper.data_dir
    data_headings = scraper.headings

    cols = [(heading, []) for heading in data_headings]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    full_path = dir_path + "/data/" + data_dir
    
    subdir_list = next(os.walk(full_path))[1]

    #loop through files/directories and call scraper on each
    if subdir_list:
        for directory in subdir_list:
            for filename in os.listdir(full_path + "/" + directory):
                if filename.endswith(".html"):
                    cols = scraper.scrape_method(full_path + "/" + directory + '/' + filename, cols)
    else:
        for filename in os.listdir(full_path):
            if filename.endswith(".html"):
                cols = scraper.scrape_method(full_path + "/" + filename, cols)

    #create dict for data
    scraper_dict = {title:column for (title, column) in cols}
    #return pandas dataframe
    return scraper_dict


def get_module_data():
    return get_data(ScraperData.MODULES.value)


def get_staff_data():
    return get_data(ScraperData.STAFF.value)


def get_timetable_data():
    return get_data(ScraperData.TIMETABLES.value)


def pop_database(scraper, database_name, username, password, hostname):
    """
    Populates a MySQL database schema with data scraped from the University website.

    Args:
        scraper (ScraperData): Scraper enum containing method and other variables used to get data for database. Can scrape
        modules, staff members or timetables.
        database_name (str): The name of the MYSQL database used.
        username (str): The username used to login to the MySQL host. 
        password (str): The password used to login to the MySQL host.
        hostname (str): The name of the database host. 

    Raises:
        OperationalError: Raised if either database is not found or login details are incorrect. 

    """

    if not isinstance(scraper, ScraperData):
        raise TypeError('scraper must be an instance of Scraper Enum')
    
    engine_url = url.URL(
        drivername='mysql+mysqldb',
        host=hostname,
        username=username,
        password=password,
        database=database_name,
        query={'charset': 'utf8'}
    )

    engine = create_engine(engine_url, encoding='utf-8')

    print("Scraping data...")
    dataframe = pd.DataFrame(get_data(scraper.value))
    print("Populating database...")
    try:
        dataframe.to_sql(con=engine, name=scraper.value.name, if_exists='replace', index=False)
        print("Table at " + database_name + " successfully created on host " +hostname+".")
    except OperationalError as e:
        print("Either database '"+database_name+"' does not exist or login/host credentials are incorrect. Please try again.")

