class Scraper:
    """
    Used to extract text data from a structured HTML source.

    Attributes:
        name: Name of the scraper.
        scrape_method: The lambda method used to scrape the data. 
        data_dir: Name of the folder inside the 'data' directory that contains relevant data.
        headings: The headings required by the user for the final data table.
    """
    def __init__(self, name, scrape_method, data_dir, headings):
        self.name = name
        self.scrape_method = scrape_method
        self.data_dir = data_dir 
        self.headings = headings 
    